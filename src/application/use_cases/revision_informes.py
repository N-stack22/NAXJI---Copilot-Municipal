from copy import deepcopy
from uuid import uuid4

from src.application.use_cases.exportar_informe import version_guardada
from src.application.use_cases.servicios_solicitud import autorizar
from src.application.use_cases.documentos import sustento_editado
from src.domain.entities.informe import VersionInforme
from src.domain.entities.solicitud import ahora
from src.domain.services.errores import ConflictoEstado, DatosInvalidos, NoAutorizado, NoEncontrado
from src.domain.services.informe_service import validar_contenido
from src.domain.services.respaldo import advertencias_respaldo, secciones_revisables
from src.domain.value_objects.estados import EstadoInforme, OrigenVersion, Rol


class RevisionInformes:
    def __init__(self, servicios, informes, revisiones, obtener, exportadores):
        self.s, self.informes, self.repo = servicios, informes, revisiones
        self.obtener, self.exportadores = obtener, exportadores

    def cargar(self, informe_id, usuario, *, revisor=False, propietario=False):
        autorizar(usuario)
        informe = self.informes.obtener_por_id(informe_id)
        if informe is None:
            raise NoEncontrado("Informe no encontrado")
        solicitud = self.s.solicitudes.obtener_por_id(informe.solicitud_id)
        if solicitud is None:
            raise NoEncontrado("Solicitud no encontrada")
        puede_revisar = (Rol.REVISOR in usuario.roles and usuario.area_id is not None
                         and usuario.area_id == solicitud.area_destino_id)
        if revisor:
            if not puede_revisar or usuario.id in {informe.creado_por, solicitud.usuario_id}:
                raise NoAutorizado("Se requiere un revisor del área de destino distinto del autor")
        elif propietario:
            autorizar(usuario, solicitud.usuario_id, escritura=True)
        elif (usuario.id != solicitud.usuario_id and Rol.ADMINISTRADOR not in usuario.roles
              and not puede_revisar):
            raise NoAutorizado("No tiene acceso a este informe")
        return informe, solicitud

    def registrar(self, informe, usuario, accion, estado, *, detalle=None, version=None):
        self.repo.registrar({"id": uuid4(), "informe_id": informe.id,
            "version_id": (version or max(informe.versiones, key=lambda v: v.numero_version)).id,
            "usuario_id": usuario.id, "accion": accion, "estado": estado,
            "fecha": ahora(), "detalle": detalle or {}})

    @staticmethod
    def vigente(informe, numero_version):
        actual = max(informe.versiones, key=lambda v: v.numero_version)
        if actual.numero_version != numero_version:
            raise ConflictoEstado("La versión cambió; recargue antes de continuar")
        return actual

    def enviar(self, informe_id, usuario, numero_version):
        with self.s.uow.transaccion():
            informe, _ = self.cargar(informe_id, usuario, propietario=True)
            self.vigente(informe, numero_version)
            if informe.estado != EstadoInforme.BORRADOR:
                raise ConflictoEstado("Solo un borrador puede enviarse a revisión")
            informe.estado = EstadoInforme.EN_REVISION
            self.informes.guardar(informe)
            self.registrar(informe, usuario, "ENVIAR_REVISION", "EN_REVISION")
        return self.historial(informe_id, usuario)

    def editar(self, informe_id, usuario, numero_version, contenido):
        with self.s.uow.transaccion():
            informe, _ = self.cargar(informe_id, usuario, revisor=True)
            anterior = self.vigente(informe, numero_version)
            if informe.estado != EstadoInforme.EN_REVISION:
                raise ConflictoEstado("Solo se edita una versión en revisión")
            validar_contenido(contenido, anterior.secciones_salida)
            claves = {s["clave"] for s in secciones_revisables(anterior)}
            if contenido.keys() - claves:
                raise DatosInvalidos("Edite únicamente las secciones del documento")
            nuevo = deepcopy(anterior.contenido)
            nuevo.update(contenido)
            version = VersionInforme(informe.id, anterior.numero_version + 1, nuevo,
                OrigenVersion.REVISION, usuario.id, titulo=anterior.titulo,
                secciones_salida=deepcopy(anterior.secciones_salida), sustento=sustento_editado(anterior, nuevo))
            informe.versiones.append(version)
            self.informes.guardar(informe)
            self.registrar(informe, usuario, "EDITAR_REVISION", "EN_REVISION")
        return self.historial(informe_id, usuario)

    def decidir(self, informe_id, usuario, numero_version, decision, motivo, comprobaciones):
        if decision not in {"APROBADO", "RECHAZADO"}:
            raise DatosInvalidos("La decisión debe ser APROBADO o RECHAZADO")
        if not motivo or not motivo.strip() or len(motivo) > 4000:
            raise DatosInvalidos("Registre un motivo de entre 1 y 4000 caracteres")
        with self.s.uow.transaccion():
            informe, _ = self.cargar(informe_id, usuario, revisor=True)
            version = self.vigente(informe, numero_version)
            if informe.estado != EstadoInforme.EN_REVISION:
                raise ConflictoEstado("La versión ya fue decidida o no está en revisión")
            if decision == "APROBADO":
                esperado = {a["seccion"] for a in advertencias_respaldo(self.obtener.proteger(informe, usuario).versiones[-1])}
                if set(comprobaciones) != esperado or any(not v.strip() or len(v) > 2000 for v in comprobaciones.values()):
                    raise DatosInvalidos("Justifique la comprobación humana de cada sección advertida")
                # No se aprueba una fuente oculta: debe hacerse accesible y volver a revisar.
                if "fuentes" in esperado:
                    raise DatosInvalidos("No puede aprobar mientras haya fuentes sin acceso")
            informe.estado = EstadoInforme(decision)
            self.informes.guardar(informe)
            self.registrar(informe, usuario, decision, decision,
                           detalle={"motivo": motivo.strip(), "comprobaciones": comprobaciones})
        return self.historial(informe_id, usuario)

    def historial(self, informe_id, usuario):
        with self.s.uow.transaccion():
            informe, solicitud = self.cargar(informe_id, usuario)
            eventos = self.repo.eventos(informe_id)
            protegido = self.obtener.proteger(informe, usuario)
            versiones = []
            for version in sorted(protegido.versiones, key=lambda v: v.numero_version):
                decisiones = [e for e in eventos if e["version_id"] == version.id and e["accion"] != "EXPORTAR"]
                versiones.append({"numero_version": version.numero_version, "id": version.id,
                    "fecha": version.created_at, "autor_id": version.creado_por,
                    "estado": decisiones[-1]["estado"] if decisiones else "NO_REGISTRADO",
                    "titulo": version.titulo, "contenido": version.contenido,
                    "secciones": secciones_revisables(version),
                    "sustento": version.sustento, "advertencias": advertencias_respaldo(version)})
            return {"informe_id": informe.id, "titulo": informe.titulo, "estado": informe.estado, "creado_por": informe.creado_por,
                    "propietario_id": solicitud.usuario_id,
                    "versiones": versiones, "eventos": eventos}

    def listar(self, usuario, limite=25, desplazamiento=0):
        autorizar(usuario)
        return self.repo.listar(usuario, limite, desplazamiento)

    def auditoria(self, usuario, limite=50, desplazamiento=0, informe_id=None):
        autorizar(usuario)
        if Rol.ADMINISTRADOR not in usuario.roles:
            raise NoAutorizado("Solo administración puede consultar la auditoría")
        return self.repo.auditoria(limite, desplazamiento, informe_id)

    def exportar(self, informe_id, numero_version, usuario, formato):
        if formato not in self.exportadores:
            raise DatosInvalidos("Formato de exportación no disponible")
        with self.s.uow.transaccion():
            informe, _ = self.cargar(informe_id, usuario)
            version = version_guardada(informe, numero_version)
            decisiones = [e for e in self.repo.eventos(informe_id) if e["version_id"] == version.id
                          and e["accion"] in {"APROBADO", "RECHAZADO", "EDITAR_REVISION", "ENVIAR_REVISION"}]
            if not decisiones or decisiones[-1]["estado"] != "APROBADO":
                raise ConflictoEstado("Solo se exporta contenido aprobado por el revisor")
            protegido = self.obtener.proteger(informe, usuario)
            version = version_guardada(protegido, numero_version)
            contenido = self.exportadores[formato].exportar(informe, version)
            self.registrar(informe, usuario, "EXPORTAR", "APROBADO", detalle={"formato": formato}, version=version)
            return contenido
