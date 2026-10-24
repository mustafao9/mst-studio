# .MST FILE SPECIFICATION
The `.mst` file format is an atomic JSON container storing the entire application design state:
- `manifest`: Versioning, application metadata, author info, hash digest.
- `database_schema`: Tables, columns, foreign keys, data types.
- `pages`: Form definitions, layout coordinates, components, and action binds.
- `security`: Users, roles, permissions scheme.
