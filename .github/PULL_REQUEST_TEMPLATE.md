## Architecture Compliance Checklist

- [ ] **Domain Isolation**: Changes maintain domain boundaries
- [ ] **Cross-Domain Communication**: Uses core infrastructure, not direct domain-to-domain links
- [ ] **Domain Dependencies**: Domain implementations don't depend on plugins
- [ ] **Output Constraints**: Links only write to allowed locations
- [ ] **Template Usage**: Template references follow the hierarchy rules
- [ ] **Security**: No sensitive information in code or config files
- [ ] **Organization**: Code organized by domain, not technical function
- [ ] **Extensibility**: Changes maintain plugin extensibility
