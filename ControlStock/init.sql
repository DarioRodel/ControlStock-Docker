CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'Homer2708**';
GRANT ALL PRIVILEGES ON control_stock.* TO 'admin'@'%';
FLUSH PRIVILEGES;
USE control_stock;

CREATE TABLE IF NOT EXISTS auth_group (
	id	integer AUTO_INCREMENT NOT NULL,
	name	varchar(150) NOT NULL UNIQUE,
	PRIMARY KEY(id )
);
CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id integer AUTO_INCREMENT NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL,
    PRIMARY KEY(id ),
    FOREIGN KEY(group_id) REFERENCES auth_group(id),
    FOREIGN KEY(permission_id) REFERENCES auth_permission(id)
);

CREATE TABLE IF NOT EXISTS auth_permission (
    id integer AUTO_INCREMENT NOT NULL,
    content_type_id integer NOT NULL,
    codename varchar(100) NOT NULL,
    name varchar(255) NOT NULL,
    PRIMARY KEY(id ),
    FOREIGN KEY(content_type_id) REFERENCES django_content_type(id)
);

CREATE TABLE IF NOT EXISTS control_categoria (
    id integer AUTO_INCREMENT NOT NULL,
    nombre varchar(100) NOT NULL UNIQUE,
    descripcion text NOT NULL,
    total_stock integer NOT NULL,
    color varchar(7) NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS control_movimientostock (
    id integer AUTO_INCREMENT NOT NULL,
    tipo varchar(10) NOT NULL,
    cantidad integer NOT NULL,
    observaciones text NOT NULL,
    fecha datetime NOT NULL,
    usuario_id integer NOT NULL,
    producto_id integer NOT NULL,
    ubicacion_destino_id integer,
    ubicacion_origen_id integer,
    PRIMARY KEY(id),
    FOREIGN KEY(producto_id) REFERENCES control_producto(id),
    FOREIGN KEY(ubicacion_destino_id) REFERENCES control_ubicacion(id),
    FOREIGN KEY(ubicacion_origen_id) REFERENCES control_ubicacion(id),
    FOREIGN KEY(usuario_id) REFERENCES control_usuariopersonalizado(id)
);

CREATE TABLE IF NOT EXISTS control_producto (
    id integer AUTO_INCREMENT NOT NULL,
    codigo_barras varchar(100) NOT NULL UNIQUE,
    nombre varchar(200) NOT NULL,
    descripcion text NOT NULL,
    precio_compra decimal NOT NULL,
    precio_venta decimal NOT NULL,
    stock_actual integer NOT NULL,
    stock_minimo integer NOT NULL,
    estado varchar(10) NOT NULL,
    imagen varchar(100),
    qr_code varchar(100),
    activo bool NOT NULL,
    creado datetime NOT NULL,
    actualizado datetime NOT NULL,
    categoria_id integer,
    ubicacion_id integer,
    PRIMARY KEY(id ),
    FOREIGN KEY(categoria_id) REFERENCES control_categoria(id) ,
    FOREIGN KEY(ubicacion_id) REFERENCES control_ubicacion(id) 
);

CREATE TABLE IF NOT EXISTS control_ubicacion (
    id integer AUTO_INCREMENT NOT NULL,
    nombre varchar(100) NOT NULL,
    codigo varchar(10) NOT NULL UNIQUE,
    descripcion text NOT NULL,
    PRIMARY KEY(id )
);

CREATE TABLE IF NOT EXISTS control_usuariopersonalizado (
    id integer AUTO_INCREMENT NOT NULL,
    password varchar(128) NOT NULL,
    last_login datetime,
    is_superuser bool NOT NULL,
    username varchar(150) NOT NULL UNIQUE,
    first_name varchar(150) NOT NULL,
    last_name varchar(150) NOT NULL,
    email varchar(254) NOT NULL,
    is_staff bool NOT NULL,
    is_active bool NOT NULL,
    date_joined datetime NOT NULL,
    rol varchar(20) NOT NULL,
    telefono varchar(20) NOT NULL,
    departamento varchar(50) NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS control_usuariopersonalizado_groups (
    id integer AUTO_INCREMENT NOT NULL,
    usuariopersonalizado_id integer NOT NULL,
    group_id integer NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(group_id) REFERENCES auth_group(id) ,
    FOREIGN KEY(usuariopersonalizado_id) REFERENCES control_usuariopersonalizado(id)
);

CREATE TABLE IF NOT EXISTS control_usuariopersonalizado_user_permissions (
    id integer AUTO_INCREMENT NOT NULL,
    usuariopersonalizado_id integer NOT NULL,
    permission_id integer NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(permission_id) REFERENCES auth_permission(id),
    FOREIGN KEY(usuariopersonalizado_id) REFERENCES control_usuariopersonalizado(id) 
);

CREATE TABLE IF NOT EXISTS django_admin_log (
    id integer AUTO_INCREMENT NOT NULL,
    object_id text,
    object_repr varchar(200) NOT NULL,
    action_flag smallint unsigned NOT NULL CHECK(action_flag >= 0),
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    action_time datetime NOT NULL,
    PRIMARY KEY(id ),
    FOREIGN KEY(content_type_id) REFERENCES django_content_type(id) ,
    FOREIGN KEY(user_id) REFERENCES control_usuariopersonalizado(id) 
);

CREATE TABLE IF NOT EXISTS django_content_type (
    id integer AUTO_INCREMENT NOT NULL,
    app_label varchar(100) NOT NULL,
    model varchar(100) NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS django_migrations (
    id integer AUTO_INCREMENT NOT NULL,
    app varchar(255) NOT NULL,
    name varchar(255) NOT NULL,
    applied datetime NOT NULL,
    PRIMARY KEY(id )
);

CREATE TABLE IF NOT EXISTS django_session (
    session_key varchar(40) NOT NULL,
    session_data text NOT NULL,
    expire_date datetime NOT NULL,
    PRIMARY KEY(session_key)
);

-- Inserts
INSERT INTO auth_group VALUES (1,'Grupo ventas');
INSERT INTO auth_group VALUES (2,'Grupo Categorias');
INSERT INTO auth_group_permissions VALUES (1,1,35);
INSERT INTO auth_group_permissions VALUES (2,1,36);
INSERT INTO auth_group_permissions VALUES (3,1,37);
INSERT INTO auth_group_permissions VALUES (4,1,38);
INSERT INTO auth_group_permissions VALUES (5,1,39);
INSERT INTO auth_group_permissions VALUES (6,2,24);
INSERT INTO auth_group_permissions VALUES (7,2,21);
INSERT INTO auth_group_permissions VALUES (8,2,22);
INSERT INTO auth_group_permissions VALUES (9,2,23);
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (1, 1, 'add_logentry', 'Can add log entry');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (2, 1, 'change_logentry', 'Can change log entry');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (3, 1, 'delete_logentry', 'Can delete log entry');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (4, 1, 'view_logentry', 'Can view log entry');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (5, 2, 'add_permission', 'Can add permission');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (6, 2, 'change_permission', 'Can change permission');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (7, 2, 'delete_permission', 'Can delete permission');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (8, 2, 'view_permission', 'Can view permission');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (9, 3, 'add_group', 'Can add group');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (10, 3, 'change_group', 'Can change group');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (11, 3, 'delete_group', 'Can delete group');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (12, 3, 'view_group', 'Can view group');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (13, 4, 'add_contenttype', 'Can add content type');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (14, 4, 'change_contenttype', 'Can change content type');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (15, 4, 'delete_contenttype', 'Can delete content type');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (16, 4, 'view_contenttype', 'Can view content type');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (17, 5, 'add_session', 'Can add session');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (18, 5, 'change_session', 'Can change session');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (19, 5, 'delete_session', 'Can delete session');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (20, 5, 'view_session', 'Can view session');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (21, 6, 'add_categoria', 'Can add Categoría');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (22, 6, 'change_categoria', 'Can change Categoría');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (23, 6, 'delete_categoria', 'Can delete Categoría');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (24, 6, 'view_categoria', 'Can view Categoría');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (25, 7, 'add_ubicacion', 'Can add Ubicación');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (26, 7, 'change_ubicacion', 'Can change Ubicación');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (27, 7, 'delete_ubicacion', 'Can delete Ubicación');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (28, 7, 'view_ubicacion', 'Can view Ubicación');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (29, 8, 'add_usuariopersonalizado', 'Can add usuario personalizado');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (30, 8, 'change_usuariopersonalizado', 'Can change usuario personalizado');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (31, 8, 'delete_usuariopersonalizado', 'Can delete usuario personalizado');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (32, 8, 'view_usuariopersonalizado', 'Can view usuario personalizado');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (33, 8, 'puede_ver_reportes', 'Puede ver reportes avanzados');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (34, 8, 'puede_gestionar_usuarios', 'Puede gestionar usuarios');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (35, 8, 'puede_eliminar_productos', 'Puede eliminar productos');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (36, 9, 'add_producto', 'Can add producto');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (37, 9, 'change_producto', 'Can change producto');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (38, 9, 'delete_producto', 'Can delete producto');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (39, 9, 'view_producto', 'Can view producto');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (40, 10, 'add_movimientostock', 'Can add Movimiento de Stock');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (41, 10, 'change_movimientostock', 'Can change Movimiento de Stock');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (42, 10, 'delete_movimientostock', 'Can delete Movimiento de Stock');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES (43, 10, 'view_movimientostock', 'Can view Movimiento de Stock');
INSERT INTO control_categoria (id, nombre, descripcion, total_stock, color) VALUES (2, 'Ordenador portatil', '', 0, '#0055ff');
INSERT INTO control_categoria (id, nombre, descripcion, total_stock, color) VALUES (3, 'Ordenadores', '', 0, '#4caf50');
INSERT INTO control_categoria (id, nombre, descripcion,total_stock, color) VALUES (4, 'Ratones', '', 0, '#4caf50');
INSERT INTO control_movimientostock (id, tipo, cantidad, observaciones, fecha, usuario_id, producto_id, ubicacion_destino_id, ubicacion_origen_id) VALUES (1, 'ENTRADA', 2, 'Registro de creación de producto', '2025-04-29 10:44:03.225998', 1, 1, NULL, NULL);
INSERT INTO control_movimientostock (id, tipo, cantidad, observaciones, fecha, usuario_id, producto_id, ubicacion_destino_id, ubicacion_origen_id) VALUES (2, 'ENTRADA', 3, 'Registro de creación de producto', '2025-04-29 12:18:28.909524', 1, 2, NULL, NULL);
INSERT INTO control_movimientostock (id, tipo, cantidad, observaciones, fecha, usuario_id, producto_id, ubicacion_destino_id, ubicacion_origen_id) VALUES (3, 'ENTRADA', 2, 'Registro de creación de producto', '2025-04-30 07:56:00.408128', 1, 3, NULL, NULL);
INSERT INTO control_producto (id, codigo_barras, nombre, descripcion, precio_compra, precio_venta, stock_actual, stock_minimo, estado, imagen, qr_code, activo, creado, actualizado, categoria_id, ubicacion_id) VALUES (1, '53535tfrsfgs', 'Patatas', 'jhsdhd', 1, 2, 2, 5, 'OK
', 'productos/Captura_de_pantalla_2025-04-23_090956.png', 'productos_qr/qr_53535tfrsfgs.png', 1, '2025-04-29 10:44:03.202750', '2025-04-29 10:44:03.232786', NULL, NULL);
INSERT INTO control_producto (id, codigo_barras, nombre, descripcion, precio_compra, precio_venta, stock_actual, stock_minimo, estado, imagen, qr_code, activo, creado, actualizado, categoria_id, ubicacion_id) VALUES (2, 'N37844002', 'Ordenador', 'El mejor ordenador HP', 300, 400, 3, 0, 'OK', 'productos/sandia_1cQhQn9.jpg', 'productos_qr/qr_N37844002.png', 1, '2025-04-29 12:18:28.886219', '2025-04-30 09:03:17.494296', 2, NULL);
INSERT INTO control_producto (id, codigo_barras, nombre, descripcion, precio_compra, precio_venta, stock_actual, stock_minimo, estado, imagen, qr_code, activo, creado, actualizado, categoria_id, ubicacion_id) VALUES (3, '25050E6QMI000161', 'Raton razer', 'sfdafsd', 30, 45, 2, 5, 'OK', 'productos/Captura_de_pantalla_2025-04-23_090910_27v9uDq.png', 'productos_qr/qr_25050E6QMI000161_ArVuYrv.png', 1, '2025-04-30 07:56:00.383192', '2025-04-30 07:56:00.413730', 4, NULL);

INSERT INTO control_usuariopersonalizado (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, rol, telefono, departamento) VALUES (1, 'pbkdf2_sha256$1000000$sWfFue8utRhymlyu3ngjyd$FL3lFy5mbZ7mTsDlEoDBp6bKoO0pLs4GAJR3fWARxkE=', '2025-04-30 09:02:46.290059', 1, 'admin', '', '', 'admin@gmail.com', 1, 1, '2025-04-29 10:29:24', 'admin', '', '');
INSERT INTO control_usuariopersonalizado (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, rol, telefono, departamento) VALUES (4, 'pbkdf2_sha256$1000000$QPFu7kCiQIWXHjwheNqN8Q$t3z70xgL0deQnYEAAmzE2UX8vxmUF4Lzx0iau/5ixXM=', '2025-04-30 08:59:47.495582', 0, 'ventas', '', '', '', 0, 1, '2025-04-30 08:59:17', 'ventas', '', '');
INSERT INTO control_usuariopersonalizado (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, rol, telefono, departamento) VALUES (5, 'pbkdf2_sha256$1000000$cMvVSe7XfP4JGOu0MY3r7q$dYpgAWGWgd6BOR6ePclcPCKytWkfGXlqKLccWbPDKN0=', '2025-04-30 09:01:12.952681', 0, 'categorias', '', '', '', 0, 1, '2025-04-30 09:00:46', 'gestor', '', '');  

INSERT INTO control_usuariopersonalizado_groups (usuariopersonalizado_id, group_id) VALUES (4, 1);
INSERT INTO control_usuariopersonalizado_groups (usuariopersonalizado_id, group_id) VALUES (5, 2);

INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 1);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 2);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 3);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 4);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 5);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 6);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 7);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 8);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 9);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 10);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 11);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 12);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 13);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 14);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 15);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 16);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 17);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 18);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 19);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 20);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 21);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 22);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 23);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 24);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 25);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 26);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 27);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 28);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 29);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 30);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 31);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 32);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 33);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 34);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 35);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 36);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 37);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 38);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 39);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 40);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 41);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 42);
INSERT INTO control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id) VALUES (1, 43);
INSERT INTO django_admin_log  VALUES (1, '2', ' (almacen)', 1, '[{"added": {}}]', 8, 1, '2025-04-29 10:32:26.342081');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (2, '3', ' (almacen)', 1, '[{"added": {}}]', 8, 1, '2025-04-29 10:52:14.131341');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (3, '3', 'innstala 2 (ventas)', 2, '[{"changed": {"fields": ["First name", "Last name", "Email address", "Telefono", "Rol", "User permissions", "Last login"]}}]', 8, 1, '2025-04-29 10:54:20.180869');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (4, '3', 'innstala 2 (ventas)', 2, '[{"changed": {"fields": ["User permissions"]}}]', 8, 1, '2025-04-29 11:02:50.138927');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (5, '2', ' (almacen)', 2, '[{"changed": {"fields": ["User permissions"]}}]', 8, 1, '2025-04-29 11:02:58.103650');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (6, '2', ' (almacen)', 2, '[]', 8, 1, '2025-04-29 11:03:38.931783');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (7, '2', ' (almacen)', 2, '[{"changed": {"fields": ["User permissions"]}}]', 8, 1, '2025-04-29 11:03:56.214498');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (8, '2', ' (almacen)', 2, '[{"changed": {"fields": ["User permissions"]}}]', 8, 1, '2025-04-29 11:04:28.307382');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (9, '1', ' (almacen)', 2, '[]', 8, 1, '2025-04-29 11:05:53.070573');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (10, '2', ' (ventas)', 2, '[{"changed": {"fields": ["Rol", "Staff status", "User permissions"]}}]', 8, 1, '2025-04-29 11:07:08.820884');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (11, '2', ' (almacen)', 2, '[{"changed": {"fields": ["Rol"]}}]', 8, 1, '2025-04-29 11:23:07.176265');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (12, '2', ' (almacen)', 2, '[{"changed": {"fields": ["User permissions"]}}]', 8, 1, '2025-04-29 11:23:14.457013');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (16, '2', ' (gestor)', 2, '[]', 8, 1, '2025-04-29 11:30:48.311509');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (17, '3', 'innstala 2 (ventas)', 2, '[{"changed": {"fields": ["User permissions"]}}]', 8, 1, '2025-04-29 11:34:18.328820');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (18, '3', 'innstala 2 (ventas)', 2, '[]', 8, 1, '2025-04-29 11:34:42.030208');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (19, '1', 'Grupo ventas', 1, '[{"added": {}}]', 3, 1, '2025-04-29 11:40:14.855140');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (20, '3', 'innstala 2 (ventas)', 2, '[{"changed": {"fields": ["Groups"]}}]', 8, 1, '2025-04-29 11:40:26.316206');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (21, '1', 'Grupo ventas', 2, '[]', 3, 1, '2025-04-29 11:50:01.004335');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (22, '2', 'Grupo Categorias', 1, '[{"added": {}}]', 3, 1, '2025-04-29 11:52:30.206566');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (23, '2', ' (gestor)', 2, '[{"changed": {"fields": ["Groups"]}}]', 8, 1, '2025-04-29 11:52:43.911501');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (24, '3', 'innstala 2 (ventas)', 3, '', 8, 1, '2025-04-30 08:58:31.902468');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (25, '2', ' (gestor)', 3, '', 8, 1, '2025-04-30 08:58:36.648431');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (26, '4', ' (almacen)', 1, '[{"added": {}}]', 8, 1, '2025-04-30 08:59:17.742040');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (27, '4', ' (ventas)', 2, '[{"changed": {"fields": ["Rol", "Groups"]}}]', 8, 1, '2025-04-30 08:59:30.965222');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (28, '5', ' (almacen)', 1, '[{"added": {}}]', 8, 1, '2025-04-30 09:00:46.681269');
INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES (29, '5', ' (gestor)', 2, '[{"changed": {"fields": ["Rol", "Groups"]}}]', 8, 1, '2025-04-30 09:00:52.529743');  

INSERT INTO django_content_type (id, app_label, model) VALUES (1, 'admin', 'logentry');
INSERT INTO django_content_type (id, app_label, model) VALUES (2, 'auth', 'permission');
INSERT INTO django_content_type (id, app_label, model) VALUES (3, 'auth', 'group');
INSERT INTO django_content_type (id, app_label, model) VALUES (4, 'contenttypes', 'contenttype');
INSERT INTO django_content_type (id, app_label, model) VALUES (5, 'sessions', 'session');
INSERT INTO django_content_type (id, app_label, model) VALUES (6, 'control', 'categoria');
INSERT INTO django_content_type (id, app_label, model) VALUES (7, 'control', 'ubicacion');
INSERT INTO django_content_type (id, app_label, model) VALUES (8, 'control', 'usuariopersonalizado');
INSERT INTO django_content_type (id, app_label, model) VALUES (9, 'control', 'producto');
INSERT INTO django_content_type (id, app_label, model) VALUES (10, 'control', 'movimientostock');  

INSERT INTO django_migrations (id, app, name, applied) VALUES (1, 'contenttypes', '0001_initial', '2025-04-29 10:26:00.533999');
INSERT INTO django_migrations (id, app, name, applied) VALUES (2, 'contenttypes', '0002_remove_content_type_name', '2025-04-29 10:26:00.543900');
INSERT INTO django_migrations (id, app, name, applied) VALUES (3, 'auth', '0001_initial', '2025-04-29 10:26:00.561886');
INSERT INTO django_migrations (id, app, name, applied) VALUES (4, 'auth', '0002_alter_permission_name_max_length', '2025-04-29 10:26:00.572740');
INSERT INTO django_migrations (id, app, name, applied) VALUES (5, 'auth', '0003_alter_user_email_max_length', '2025-04-29 10:26:00.580056');
INSERT INTO django_migrations (id, app, name, applied) VALUES (6, 'auth', '0004_alter_user_username_opts', '2025-04-29 10:26:00.587157');
INSERT INTO django_migrations (id, app, name, applied) VALUES (7, 'auth', '0005_alter_user_last_login_null', '2025-04-29 10:26:00.600959');
INSERT INTO django_migrations (id, app, name, applied) VALUES (8, 'auth', '0006_require_contenttypes_0002', '2025-04-29 10:26:00.607005');
INSERT INTO django_migrations (id, app, name, applied) VALUES (9, 'auth', '0007_alter_validators_add_error_messages', '2025-04-29 10:26:00.615125');
INSERT INTO django_migrations (id, app, name, applied) VALUES (10, 'auth', '0008_alter_user_username_max_length', '2025-04-29 10:26:00.621794');
INSERT INTO django_migrations (id, app, name, applied) VALUES (11, 'auth', '0009_alter_user_last_name_max_length', '2025-04-29 10:26:00.630007');
INSERT INTO django_migrations (id, app, name, applied) VALUES (12, 'auth', '0010_alter_group_name_max_length', '2025-04-29 10:26:00.638283');
INSERT INTO django_migrations (id, app, name, applied) VALUES (13, 'auth', '0011_update_proxy_permissions', '2025-04-29 10:26:00.646320');
INSERT INTO django_migrations (id, app, name, applied) VALUES (14, 'auth', '0012_alter_user_first_name_max_length', '2025-04-29 10:26:00.653613');
INSERT INTO django_migrations (id, app, name, applied) VALUES (15, 'control', '0001_initial', '2025-04-29 10:26:00.688532');
INSERT INTO django_migrations (id, app, name, applied) VALUES (16, 'admin', '0001_initial', '2025-04-29 10:26:00.704509');
INSERT INTO django_migrations (id, app, name, applied) VALUES (17, 'admin', '0002_logentry_remove_auto_add', '2025-04-29 10:26:00.718427');
INSERT INTO django_migrations (id, app, name, applied) VALUES (18, 'admin', '0003_logentry_add_action_flag_choices', '2025-04-29 10:26:00.728993');
INSERT INTO django_migrations (id, app, name, applied) VALUES (19, 'sessions', '0001_initial', '2025-04-29 10:26:00.740916');
INSERT INTO django_migrations (id, app, name, applied) VALUES (20, 'control', '0002_alter_usuariopersonalizado_rol', '2025-04-29 11:25:38.540067');
INSERT INTO django_migrations (id, app, name, applied) VALUES (21, 'control', '0003_usuariopersonalizado_tutorial_completado_and_more', '2025-04-30 07:18:50.244404');
INSERT INTO django_migrations (id, app, name, applied) VALUES (22, 'control', '0004_remove_usuariopersonalizado_tutorial_completado_and_more', '2025-04-30 08:29:50.826972');

INSERT INTO django_session (session_key, session_data, expire_date) VALUES ('6rwladxbtd6fmxs34rjip1p0n2dh1lnt', '.eJxVjEEOwiAURO_C2hAoqYBL956BfOZ_pGrapLSrxrtrky50O--92VSidalpbTKngdVFWXX63TLhKeMO-EHjfdKYxmUest4VfdCmbxPL63q4fweVWv3WKF1nbe4AZEjJFAIRC8Seo_WegRCZRJzxcDHCFCqmZ8fBBd9D1PsDMxI5sQ:1uA3L4:vEWSRbF8egEqXu-68v_nx0wuP6Ok5TmZExxkK45fRDw', '2025-05-14 09:02:46.295003');

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON auth_group_permissions (group_id);
CREATE UNIQUE INDEX auth_group_permissions_group_id_permission_id_0cd325b0_uniq ON auth_group_permissions (group_id, permission_id);
CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON auth_group_permissions (permission_id);

CREATE INDEX auth_permission_content_type_id_2f476e4b ON auth_permission (content_type_id);
CREATE UNIQUE INDEX auth_permission_content_type_id_codename_01ab375a_uniq ON auth_permission (content_type_id, codename);

CREATE INDEX control_movimientostock_producto_id_182b01f2 ON control_movimientostock (producto_id);
CREATE INDEX control_movimientostock_ubicacion_destino_id_ecce5e08 ON control_movimientostock (ubicacion_destino_id);
CREATE INDEX control_movimientostock_ubicacion_origen_id_86306ecc ON control_movimientostock (ubicacion_origen_id);
CREATE INDEX control_movimientostock_usuario_id_c894caab ON control_movimientostock (usuario_id);

CREATE INDEX control_pro_categor_927a39_idx ON control_producto (categoria_id);
CREATE INDEX control_pro_codigo__a1add4_idx ON control_producto (codigo_barras);
CREATE INDEX control_pro_estado_acbccf_idx ON control_producto (estado);
CREATE INDEX control_pro_nombre_212dde_idx ON control_producto (nombre);
CREATE INDEX control_producto_categoria_id_1d6b6eed ON control_producto (categoria_id);
CREATE INDEX control_producto_ubicacion_id_0ceaca33 ON control_producto (ubicacion_id);

CREATE INDEX control_usuariopersonalizado_groups_group_id_cd360998 ON control_usuariopersonalizado_groups (group_id);
CREATE INDEX control_up_g_up_id_b8c411ec ON control_usuariopersonalizado_groups (usuariopersonalizado_id);
CREATE UNIQUE INDEX control_up_g_up_id_g_id_def660d5_uniq ON control_usuariopersonalizado_groups (usuariopersonalizado_id, group_id);

CREATE INDEX control_up_u_pm_pm_id_72d978a9 ON control_usuariopersonalizado_user_permissions (permission_id);
CREATE INDEX control_up_u_pm_up_id_2b6583be ON control_usuariopersonalizado_user_permissions (usuariopersonalizado_id);
CREATE UNIQUE INDEX control_up_u_pm_up_id_pm_id_92e18e3b_uniq ON control_usuariopersonalizado_user_permissions (usuariopersonalizado_id, permission_id);

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON django_admin_log (content_type_id);
CREATE INDEX django_admin_log_user_id_c564eba6 ON django_admin_log (user_id);

CREATE INDEX django_session_expire_date_a5c62663 ON django_session (expire_date);
