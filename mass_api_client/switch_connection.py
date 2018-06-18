from .resources import BaseResource


class SwitchConnection:
    def __init__(self, resource, connection_alias):
        self.resource = resource
        self._connection_alias = connection_alias

    def __enter__(self):
        if issubclass(self.resource, BaseResource):
            modified = self._create_modified_base()
        else:
            raise ValueError("'{}' is not a mass_api_client resource.".format(type(self.resource)))

        modified.__name__ = "Modified{}".format(self.resource.__name__)
        return modified

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _create_modified_base(self):
        class ModifiedResource(self.resource):
            _connection_alias = self._connection_alias

        return ModifiedResource

