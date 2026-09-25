-- ============================================================
-- NAXJI - ESTADO ACTUAL DE BASE DE DATOS
-- Supabase / PostgreSQL
-- Estado alcanzado hasta el final del PASO 3
-- ============================================================

-- IMPORTANTE:
-- 1. auth.users es administrado por Supabase Auth.
-- 2. Todavía NO se han creado políticas RLS.
-- 3. RLS sí está activado en las tablas.
-- 4. Todavía NO se implementaron tablas de PMV2/RAG ni PMV3.
-- 5. Los únicos datos iniciales confirmados son:
--      - 4 roles
--      - 4 tipos de informe
-- ============================================================

create extension if not exists pgcrypto;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create table if not exists public.areas_municipales (
    id uuid primary key default gen_random_uuid(),
    codigo varchar(30) unique,
    nombre varchar(180) not null,
    descripcion text,
    area_padre_id uuid references public.areas_municipales(id) on delete set null,
    activo boolean not null default true,
    created_at timestamptz not null default now(),
    constraint chk_area_nombre check (length(trim(nombre)) > 0)
);

create table if not exists public.tipos_informe (
    id uuid primary key default gen_random_uuid(),
    codigo varchar(30) not null unique,
    nombre varchar(100) not null,
    descripcion text,
    activo boolean not null default true,
    created_at timestamptz not null default now(),
    constraint chk_tipo_informe_nombre check (length(trim(nombre)) > 0)
);

create table if not exists public.normativas (
    id uuid primary key default gen_random_uuid(),
    codigo varchar(100),
    titulo text not null,
    tipo varchar(50) not null,
    numero varchar(50),
    fecha_publicacion date,
    fecha_inicio_vigencia date,
    fecha_fin_vigencia date,
    url_fuente text,
    descripcion text,
    activo boolean not null default true,
    created_at timestamptz not null default now(),
    constraint chk_normativa_tipo check (tipo in ('ORDENANZA','LEY','DECRETO','DIRECTIVA','REGLAMENTO','RESOLUCION','OTRO')),
    constraint chk_normativa_titulo check (length(trim(titulo)) > 0),
    constraint chk_fechas_normativa check (
        fecha_fin_vigencia is null or fecha_inicio_vigencia is null or fecha_fin_vigencia >= fecha_inicio_vigencia
    )
);

create unique index if not exists uq_normativas_codigo
on public.normativas(codigo)
where codigo is not null;

create table if not exists public.roles (
    id uuid primary key default gen_random_uuid(),
    codigo varchar(30) not null unique,
    nombre varchar(80) not null,
    descripcion text,
    activo boolean not null default true,
    created_at timestamptz not null default now()
);

create table if not exists public.perfiles (
    id uuid primary key references auth.users(id) on delete cascade,
    nombres varchar(100) not null,
    apellidos varchar(150) not null,
    cargo varchar(150),
    area_id uuid references public.areas_municipales(id) on delete set null,
    activo boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint chk_perfil_nombres check (length(trim(nombres)) > 0),
    constraint chk_perfil_apellidos check (length(trim(apellidos)) > 0)
);

create table if not exists public.usuario_roles (
    usuario_id uuid not null references public.perfiles(id) on delete cascade,
    rol_id uuid not null references public.roles(id) on delete cascade,
    asignado_por uuid references public.perfiles(id) on delete set null,
    created_at timestamptz not null default now(),
    primary key (usuario_id, rol_id)
);

create table if not exists public.plantillas (
    id uuid primary key default gen_random_uuid(),
    nombre varchar(150) not null,
    tipo_informe_id uuid not null references public.tipos_informe(id) on delete restrict,
    area_id uuid references public.areas_municipales(id) on delete set null,
    version integer not null default 1,
    descripcion text,
    activa boolean not null default true,
    creado_por uuid references public.perfiles(id) on delete set null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint chk_plantilla_version check (version > 0),
    constraint uq_plantilla_nombre_version unique (nombre, version)
);

create table if not exists public.campos_plantilla (
    id uuid primary key default gen_random_uuid(),
    plantilla_id uuid not null references public.plantillas(id) on delete cascade,
    clave varchar(80) not null,
    etiqueta varchar(150) not null,
    tipo_dato varchar(30) not null,
    obligatorio boolean not null default false,
    orden integer not null,
    configuracion jsonb not null default '{}'::jsonb,
    activo boolean not null default true,
    created_at timestamptz not null default now(),
    constraint chk_campo_tipo check (tipo_dato in ('text','textarea','date','number','boolean','select')),
    constraint chk_campo_orden check (orden > 0),
    constraint uq_campo_plantilla unique (plantilla_id, clave)
);

create table if not exists public.solicitudes (
    id uuid primary key default gen_random_uuid(),
    usuario_id uuid not null references public.perfiles(id) on delete restrict,
    asunto text not null,
    tipo_informe_id uuid references public.tipos_informe(id) on delete set null,
    plantilla_id uuid references public.plantillas(id) on delete set null,
    area_origen_id uuid references public.areas_municipales(id) on delete set null,
    area_destino_id uuid references public.areas_municipales(id) on delete set null,
    estado varchar(30) not null default 'BORRADOR',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint chk_solicitud_estado check (estado in ('BORRADOR','LISTA_PARA_GENERAR','PROCESANDO','GENERADA','CANCELADA')),
    constraint chk_solicitud_asunto check (length(trim(asunto)) > 0)
);

create table if not exists public.solicitud_valores (
    id uuid primary key default gen_random_uuid(),
    solicitud_id uuid not null references public.solicitudes(id) on delete cascade,
    campo_plantilla_id uuid not null references public.campos_plantilla(id) on delete restrict,
    valor jsonb not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint uq_solicitud_campo unique (solicitud_id, campo_plantilla_id)
);

create table if not exists public.predicciones_ia (
    id uuid primary key default gen_random_uuid(),
    solicitud_id uuid not null references public.solicitudes(id) on delete cascade,
    tipo_informe_predicho_id uuid references public.tipos_informe(id) on delete set null,
    area_destino_predicha_id uuid references public.areas_municipales(id) on delete set null,
    confianza_tipo numeric(5,4),
    confianza_area numeric(5,4),
    modelo varchar(150) not null,
    version_modelo varchar(100),
    parametros jsonb not null default '{}'::jsonb,
    resultado_validacion varchar(30) not null default 'PENDIENTE',
    validado_por uuid references public.perfiles(id) on delete set null,
    validado_at timestamptz,
    created_at timestamptz not null default now(),
    constraint chk_confianza_tipo check (confianza_tipo is null or confianza_tipo between 0 and 1),
    constraint chk_confianza_area check (confianza_area is null or confianza_area between 0 and 1),
    constraint chk_prediccion_validacion check (resultado_validacion in ('PENDIENTE','ACEPTADA','CORREGIDA','RECHAZADA'))
);

create table if not exists public.prediccion_normativas (
    id uuid primary key default gen_random_uuid(),
    prediccion_id uuid not null references public.predicciones_ia(id) on delete cascade,
    normativa_id uuid not null references public.normativas(id) on delete restrict,
    confianza numeric(5,4),
    orden integer,
    aceptada boolean,
    created_at timestamptz not null default now(),
    constraint chk_normativa_confianza check (confianza is null or confianza between 0 and 1),
    constraint chk_normativa_orden check (orden is null or orden > 0),
    constraint uq_prediccion_normativa unique (prediccion_id, normativa_id)
);

create table if not exists public.informes (
    id uuid primary key default gen_random_uuid(),
    solicitud_id uuid not null unique references public.solicitudes(id) on delete restrict,
    plantilla_id uuid not null references public.plantillas(id) on delete restrict,
    titulo text,
    estado varchar(30) not null default 'BORRADOR',
    creado_por uuid references public.perfiles(id) on delete set null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint chk_informe_estado check (estado in ('BORRADOR','EN_REVISION','OBSERVADO','APROBADO','RECHAZADO','ARCHIVADO'))
);

create table if not exists public.versiones_informe (
    id uuid primary key default gen_random_uuid(),
    informe_id uuid not null references public.informes(id) on delete cascade,
    numero_version integer not null,
    contenido jsonb not null,
    origen varchar(30) not null,
    creado_por uuid references public.perfiles(id) on delete set null,
    modelo_ia varchar(150),
    prompt_version varchar(50),
    resumen_cambios text,
    created_at timestamptz not null default now(),
    constraint chk_version_numero check (numero_version > 0),
    constraint chk_version_origen check (origen in ('IA','USUARIO','REVISION','SISTEMA')),
    constraint uq_informe_version unique (informe_id, numero_version)
);

create index if not exists idx_perfiles_area on public.perfiles(area_id);
create index if not exists idx_usuario_roles_rol on public.usuario_roles(rol_id);
create index if not exists idx_plantillas_tipo on public.plantillas(tipo_informe_id);
create index if not exists idx_plantillas_area on public.plantillas(area_id);
create index if not exists idx_campos_plantilla on public.campos_plantilla(plantilla_id);
create index if not exists idx_solicitudes_usuario on public.solicitudes(usuario_id);
create index if not exists idx_solicitudes_estado on public.solicitudes(estado);
create index if not exists idx_solicitudes_tipo on public.solicitudes(tipo_informe_id);
create index if not exists idx_predicciones_solicitud on public.predicciones_ia(solicitud_id);
create index if not exists idx_prediccion_normativas_pred on public.prediccion_normativas(prediccion_id);
create index if not exists idx_informes_estado on public.informes(estado);
create index if not exists idx_versiones_informe on public.versiones_informe(informe_id);

drop trigger if exists trg_perfiles_updated_at on public.perfiles;
create trigger trg_perfiles_updated_at before update on public.perfiles for each row execute function public.set_updated_at();

drop trigger if exists trg_plantillas_updated_at on public.plantillas;
create trigger trg_plantillas_updated_at before update on public.plantillas for each row execute function public.set_updated_at();

drop trigger if exists trg_solicitudes_updated_at on public.solicitudes;
create trigger trg_solicitudes_updated_at before update on public.solicitudes for each row execute function public.set_updated_at();

drop trigger if exists trg_solicitud_valores_updated_at on public.solicitud_valores;
create trigger trg_solicitud_valores_updated_at before update on public.solicitud_valores for each row execute function public.set_updated_at();

drop trigger if exists trg_informes_updated_at on public.informes;
create trigger trg_informes_updated_at before update on public.informes for each row execute function public.set_updated_at();

alter table public.areas_municipales enable row level security;
alter table public.tipos_informe enable row level security;
alter table public.normativas enable row level security;
alter table public.roles enable row level security;
alter table public.perfiles enable row level security;
alter table public.usuario_roles enable row level security;
alter table public.plantillas enable row level security;
alter table public.campos_plantilla enable row level security;
alter table public.solicitudes enable row level security;
alter table public.solicitud_valores enable row level security;
alter table public.predicciones_ia enable row level security;
alter table public.prediccion_normativas enable row level security;
alter table public.informes enable row level security;
alter table public.versiones_informe enable row level security;

insert into public.roles (codigo, nombre, descripcion) values
('ADMINISTRADOR','Administrador','Gestiona usuarios, roles y configuración general.'),
('FUNCIONARIO','Funcionario','Registra solicitudes y elabora documentos.'),
('REVISOR','Revisor','Revisa y formula observaciones sobre los documentos.'),
('APROBADOR','Aprobador','Realiza la aprobación final de documentos.')
on conflict (codigo) do nothing;

insert into public.tipos_informe (codigo, nombre, descripcion) values
('INFORME_TECNICO','Informe Técnico','Documento de análisis técnico.'),
('INFORME_LEGAL','Informe Legal','Documento de análisis jurídico o normativo.'),
('INFORME_INSPECCION','Informe de Inspección','Documento generado como resultado de una inspección.'),
('MEMORANDO','Memorando','Documento de comunicación administrativa interna.')
on conflict (codigo) do nothing;

-- ============================================================
-- FIN DEL ESTADO ACTUAL
-- ============================================================
