def register():
    from core.registry import PackageRegistry
    PackageRegistry.register_package("linguistics", __name__)
