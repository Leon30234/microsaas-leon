# León | microsaas

Micro-SaaS con gestión de clientes, productos y pedidos.

## Instalación

```bash
pip install -r requirements.txt
python app.py
```

Accede en: http://localhost:5000

## Credenciales por defecto

- Usuario: `León`
- Contraseña: `León`

## Estructura

```
microsaas/
├── app.py                  # Aplicación Flask
├── requirements.txt
├── static/
│   ├── css/style.css
│   └── logo.png            # ← Coloca aquí tu logo
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── clientes.html
    ├── cliente_form.html
    ├── productos.html
    ├── producto_form.html
    ├── pedidos.html
    ├── pedido_form.html
    └── pedido_ver.html
```

## Notas

- El logo debe colocarse en `static/logo.png`
- La base de datos SQLite se crea automáticamente en `microsaas.db`
