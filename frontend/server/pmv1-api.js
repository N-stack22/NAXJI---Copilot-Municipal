import http from "node:http";
import { randomUUID } from "node:crypto";

const PORT = 8000;

const USUARIOS = {
  "demo-funcionario": {
    id: "11111111-1111-1111-1111-111111111111",
    roles: ["FUNCIONARIO"],
    area_id: "aaaa1111-0000-0000-0000-000000000001",
    activo: true,
  },
  "demo-admin": {
    id: "22222222-2222-2222-2222-222222222222",
    roles: ["ADMINISTRADOR"],
    area_id: "aaaa1111-0000-0000-0000-000000000001",
    activo: true,
  },
  "demo-revisor": {
    id: "11111111-1111-1111-1111-111111111111",
    roles: ["REVISOR"],
    area_id: "aaaa1111-0000-0000-0000-000000000001",
    activo: true,
  },
  "demo-aprobador": {
    id: "11111111-1111-1111-1111-111111111111",
    roles: ["APROBADOR"],
    area_id: "aaaa1111-0000-0000-0000-000000000001",
    activo: true,
  },
  "demo-otro": {
    id: "33333333-3333-3333-3333-333333333333",
    roles: ["FUNCIONARIO"],
    area_id: "aaaa1111-0000-0000-0000-000000000002",
    activo: true,
  },
};

const TIPOS = [
  { id: "t1111111-0000-0000-0000-000000000001", codigo: "INFORME_TECNICO", nombre: "Informe Técnico", activo: true },
  { id: "t1111111-0000-0000-0000-000000000002", codigo: "INFORME_LEGAL", nombre: "Informe Legal", activo: true },
  { id: "t1111111-0000-0000-0000-000000000003", codigo: "INFORME_INSPECCION", nombre: "Informe de Inspección", activo: true },
  { id: "t1111111-0000-0000-0000-000000000004", codigo: "MEMORANDO", nombre: "Memorando", activo: true },
];

const AREAS = [
  { id: "aaaa1111-0000-0000-0000-000000000001", codigo: "AREA_ECOLOGIA", nombre: "Subgerencia de Ecología y Medio Ambiente", activo: true },
  { id: "aaaa1111-0000-0000-0000-000000000002", codigo: "AREA_SERVICIOS_PUBLICOS", nombre: "Gerencia de Servicios Públicos", activo: true },
  { id: "aaaa1111-0000-0000-0000-000000000003", codigo: "AREA_DESARROLLO_URBANO", nombre: "Gerencia de Desarrollo Urbano", activo: true },
  { id: "aaaa1111-0000-0000-0000-000000000004", codigo: "AREA_DESARROLLO_ECONOMICO", nombre: "Gerencia de Desarrollo Económico", activo: true },
  { id: "aaaa1111-0000-0000-0000-000000000005", codigo: "AREA_RIESGO_DESASTRES", nombre: "Subgerencia de Gestión del Riesgo de Desastres", activo: true },
  { id: "aaaa1111-0000-0000-0000-000000000006", codigo: "AREA_ASESORIA_JURIDICA", nombre: "Oficina de Asesoría Jurídica", activo: true },
];

const plantillas = TIPOS.map((tipo, indice) => ({
  id: `p1111111-0000-0000-0000-00000000000${indice + 1}`,
  nombre: `${tipo.nombre} (DEMO)`,
  tipo_informe_id: tipo.id,
  area_id: null,
  version: 1,
  activa: true,
}));

const campos = [];
for (const plantilla of plantillas) {
  const definiciones = [
    ["antecedentes", "Antecedentes", "textarea", true],
    ["detalle", "Análisis / detalle", "text", true],
    ["fecha", "Fecha", "date", false],
    ["cantidad", "Cantidad", "number", false],
    ["verificado", "Verificado", "boolean", false],
    ["prioridad", "Prioridad", "select", false],
  ];

  definiciones.forEach(([clave, etiqueta, tipo_dato, obligatorio], orden) => {
    campos.push({
      id: randomUUID(),
      plantilla_id: plantilla.id,
      clave,
      etiqueta,
      tipo_dato,
      obligatorio,
      orden: orden + 1,
      configuracion: tipo_dato === "select" ? { opciones: ["NORMAL", "ALTA"] } : {},
      activo: true,
    });
  });
}

const solicitudes = new Map();
const predicciones = new Map();
const informes = new Map();

const ahora = () => new Date().toISOString();

const leerCuerpo = async (req) => {
  const chunks = [];
  for await (const chunk of req) {
    chunks.push(chunk);
  }
  const raw = Buffer.concat(chunks).toString("utf8");
  return raw ? JSON.parse(raw) : {};
};

const enviar = (res, codigo, cuerpo) => {
  res.writeHead(codigo, {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Authorization, Content-Type",
    "Access-Control-Allow-Methods": "GET, POST, PUT, OPTIONS",
  });
  res.end(JSON.stringify(cuerpo));
};

const autenticar = (req) => {
  const header = req.headers.authorization || "";
  const token = header.replace(/^Bearer\s+/i, "").trim();
  return USUARIOS[token] || null;
};

const puedeEscribir = (usuario) =>
  usuario.roles.includes("FUNCIONARIO") || usuario.roles.includes("ADMINISTRADOR");

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === "OPTIONS") {
      enviar(res, 204, {});
      return;
    }

    const url = new URL(req.url, `http://127.0.0.1:${PORT}`);
    const ruta = url.pathname.replace(/\/$/, "") || "/";

    if (req.method === "GET" && ruta === "/health") {
      enviar(res, 200, { status: "ok", service: "NAXJI API (demo local PMV 1)" });
      return;
    }

    const usuario = autenticar(req);
    if (!usuario) {
      enviar(res, 401, { detail: "Autenticación requerida o token inválido" });
      return;
    }

    if (req.method === "GET" && ruta === "/auth/me") {
      enviar(res, 200, usuario);
      return;
    }

    if (req.method === "GET" && ruta === "/tipos-informe") {
      enviar(res, 200, TIPOS);
      return;
    }

    if (req.method === "GET" && ruta === "/areas") {
      enviar(res, 200, AREAS);
      return;
    }

    if (req.method === "GET" && ruta === "/plantillas") {
      const tipo = url.searchParams.get("tipo_informe_id");
      const lista = tipo
        ? plantillas.filter((item) => item.tipo_informe_id === tipo)
        : plantillas;
      enviar(res, 200, lista);
      return;
    }

    const camposMatch = ruta.match(/^\/plantillas\/([^/]+)\/campos$/);
    if (req.method === "GET" && camposMatch) {
      enviar(res, 200, campos.filter((campo) => campo.plantilla_id === camposMatch[1]));
      return;
    }

    if (req.method === "POST" && ruta === "/solicitudes") {
      if (!puedeEscribir(usuario)) {
        enviar(res, 403, { detail: "El rol no permite elaborar informes" });
        return;
      }

      const body = await leerCuerpo(req);
      const solicitud = {
        id: randomUUID(),
        usuario_id: usuario.id,
        asunto: body.asunto,
        tipo_informe_id: body.tipo_informe_id || null,
        plantilla_id: body.plantilla_id || null,
        area_origen_id: body.area_origen_id || null,
        area_destino_id: body.area_destino_id || null,
        estado: "BORRADOR",
        valores: [],
        created_at: ahora(),
        updated_at: ahora(),
      };
      solicitudes.set(solicitud.id, solicitud);
      enviar(res, 201, solicitud);
      return;
    }

    const solicitudMatch = ruta.match(/^\/solicitudes\/([^/]+)$/);
    if (solicitudMatch) {
      const solicitud = solicitudes.get(solicitudMatch[1]);
      if (!solicitud) {
        enviar(res, 404, { detail: "Solicitud no encontrada" });
        return;
      }

      if (req.method === "GET") {
        enviar(res, 200, solicitud);
        return;
      }

      if (req.method === "PUT") {
        if (!puedeEscribir(usuario)) {
          enviar(res, 403, { detail: "El rol no permite elaborar informes" });
          return;
        }

        const body = await leerCuerpo(req);
        Object.assign(solicitud, body, { updated_at: ahora() });
        enviar(res, 200, solicitud);
        return;
      }
    }

    const valoresMatch = ruta.match(/^\/solicitudes\/([^/]+)\/valores$/);
    if (req.method === "PUT" && valoresMatch) {
      const solicitud = solicitudes.get(valoresMatch[1]);
      if (!solicitud) {
        enviar(res, 404, { detail: "Solicitud no encontrada" });
        return;
      }

      const body = await leerCuerpo(req);
      solicitud.valores = (body.valores || []).map((valor) => ({
        id: randomUUID(),
        solicitud_id: solicitud.id,
        campo_plantilla_id: valor.campo_plantilla_id,
        valor: valor.valor,
        created_at: ahora(),
        updated_at: ahora(),
      }));
      solicitud.updated_at = ahora();
      enviar(res, 200, solicitud);
      return;
    }

    const predecirMatch = ruta.match(/^\/solicitudes\/([^/]+)\/predecir-contexto$/);
    if (req.method === "POST" && predecirMatch) {
      const solicitud = solicitudes.get(predecirMatch[1]);
      if (!solicitud) {
        enviar(res, 404, { detail: "Solicitud no encontrada" });
        return;
      }

      const tipo = TIPOS.find((item) => item.id === solicitud.tipo_informe_id) || TIPOS[2];
      const area = AREAS.find((item) => item.id === solicitud.area_destino_id) || AREAS[0];
      const prediccion = {
        id: randomUUID(),
        solicitud_id: solicitud.id,
        modelo: "MOCK_CONTEXT_PREDICTOR",
        version_modelo: "demo-1",
        es_mock: true,
        resultado_validacion: "PENDIENTE",
        validado_por: null,
        validado_at: null,
        tipo_informe: { id: tipo.id, codigo: tipo.codigo, nombre: tipo.nombre, confianza: 0.91 },
        area_destino: { id: area.id, codigo: area.codigo, nombre: area.nombre, confianza: 0.87 },
        normativas: [
          {
            normativa_id: "n1111111-0000-0000-0000-000000000001",
            codigo: "NORM_RESIDUOS",
            titulo: "Normativa municipal sobre gestión de residuos sólidos",
            confianza: 0.82,
            orden: 1,
            aceptada: null,
          },
        ],
      };
      predicciones.set(solicitud.id, prediccion);
      enviar(res, 200, prediccion);
      return;
    }

    const validarMatch = ruta.match(/^\/solicitudes\/([^/]+)\/validar-prediccion$/);
    if (req.method === "POST" && validarMatch) {
      const prediccion = predicciones.get(validarMatch[1]);
      if (!prediccion) {
        enviar(res, 404, { detail: "No hay una predicción para validar" });
        return;
      }

      const body = await leerCuerpo(req);
      prediccion.resultado_validacion = body.resultado;
      prediccion.validado_por = usuario.id;
      prediccion.validado_at = ahora();
      enviar(res, 200, prediccion);
      return;
    }

    const generarMatch = ruta.match(/^\/solicitudes\/([^/]+)\/generar-borrador$/);
    if (req.method === "POST" && generarMatch) {
      const solicitud = solicitudes.get(generarMatch[1]);
      const prediccion = predicciones.get(generarMatch[1]);
      if (!solicitud) {
        enviar(res, 404, { detail: "Solicitud no encontrada" });
        return;
      }
      if (!prediccion || !["ACEPTADA", "CORREGIDA"].includes(prediccion.resultado_validacion)) {
        enviar(res, 409, { detail: "Debe confirmar o corregir el contexto antes de generar" });
        return;
      }

      const body = await leerCuerpo(req);
      const informe = {
        informe_id: randomUUID(),
        solicitud_id: solicitud.id,
        plantilla_id: solicitud.plantilla_id,
        titulo: solicitud.asunto,
        estado: "BORRADOR",
        version_id: randomUUID(),
        numero_version: 1,
        contenido: {
          antecedentes: "Borrador generado a partir de los datos registrados.",
          desarrollo: "Desarrollo estructurado según la plantilla institucional.",
          conclusiones: "Conclusiones preliminares para revisión del funcionario.",
          instrucciones: body.instrucciones || "",
        },
        origen: "IA",
        modelo_ia: "MOCK_GENERADOR_BORRADOR",
        created_at: ahora(),
        updated_at: ahora(),
      };
      informes.set(informe.informe_id, informe);
      solicitud.estado = "GENERADA";
      enviar(res, 201, informe);
      return;
    }

    const informeMatch = ruta.match(/^\/informes\/([^/]+)$/);
    if (informeMatch) {
      const informe = informes.get(informeMatch[1]);
      if (!informe) {
        enviar(res, 404, { detail: "Informe no encontrado" });
        return;
      }

      if (req.method === "GET") {
        enviar(res, 200, informe);
        return;
      }

      if (req.method === "PUT") {
        const body = await leerCuerpo(req);
        if (body.numero_version !== informe.numero_version) {
          enviar(res, 409, { detail: "La versión enviada no es la más reciente" });
          return;
        }

        informe.contenido = body.contenido;
        informe.titulo = body.titulo || informe.titulo;
        informe.numero_version += 1;
        informe.origen = "USUARIO";
        informe.version_id = randomUUID();
        informe.updated_at = ahora();
        enviar(res, 200, informe);
        return;
      }
    }

    enviar(res, 404, { detail: "Ruta no encontrada" });
  } catch (error) {
    enviar(res, 500, { detail: error.message || "Error interno del servidor" });
  }
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`API demo PMV 1 en http://127.0.0.1:${PORT}`);
  console.log("Mismo contrato que el backend de Nathalie. Use token demo-funcionario.");
});
