from .resources import BaseResource, BaseWithSubclasses


class switch_connection:
    def __init__(self, resource, connection_alias):
        self.resource = resource
        self.connection_alias = connection_alias

    def __enter__(self):
        if issubclass(self.resource, BaseWithSubclasses):
            modified = self._create_modified_base_with_subclasses()
        elif issubclass(self.resource, BaseResource):
            modified = self._create_modified_base()
        else:
            raise ValueError("'{}' is not a mass_api_client resource.".format(type(self.resource)))

        modified.__name__ = "Modified{}".format(self.resource.__name__)
        return modified

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _create_modified_base(self):
        class ModifiedResource(self.resource):
            connection_alias = self.connection_alias

        return ModifiedResource

    def _create_modified_base_with_subclasses(self):
        class ModifiedResource(self.resource):
            connection_alias = self.connection_alias
            _unmodified_cls = self.resource

            @classmethod
            def _create_instance_from_data(cls, data):
                subcls = cls._unmodified_cls._search_subclass(data['_cls'])
                return subcls(subcls.connection_alias, **data)

            @classmethod
            def _deserialize(cls, data, many=False):
                if many:
                    return [cls._deserialize(item) for item in data]

                subcls = cls._unmodified_cls._search_subclass(data['_cls'])

                return subcls._deserialize(data, many)

        return ModifiedResource

