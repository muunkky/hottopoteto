# Architecture Principles Quick Reference

1. **Domain Isolation**: Links limited to single domain
2. **Domain Dependencies**: Domains ↛ plugins (domains never depend on plugins)
3. **Cross-Domain Communication**: Only through core infrastructure
4. **Output Constraints**: Links write only to domain or root output folders
5. **Template Hierarchy**: Recipe templates can reference others, text templates cannot
6. **Security**: No credentials in code
7. **Organization**: Code organized by domain, not technical function
8. **Extensibility**: System extensible without modifying core code
