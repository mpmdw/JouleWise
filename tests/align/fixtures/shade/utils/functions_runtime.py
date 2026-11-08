"""Original stdlib fixture implementing the upstream function-runtime shape."""

import inspect
from dataclasses import dataclass
from typing import Annotated, get_origin, get_type_hints


@dataclass
class Depends:
    env_dependency: object

    def extract_dep_from_env(self, environment):
        return (self.env_dependency(environment) if callable(self.env_dependency)
                else getattr(environment, self.env_dependency))


@dataclass
class FunctionCall:
    function: str
    args: dict
    id: str | None = None


class Parameters:
    def __init__(self, function, dependencies):
        self.signature = inspect.signature(function)
        hints = get_type_hints(function, include_extras=True)
        self.arguments = {name: (hints.get(name, str), parameter)
                          for name, parameter in self.signature.parameters.items()
                          if name not in dependencies}

    def model_json_schema(self):
        types = {str: "string", int: "integer", bool: "boolean"}
        properties = {}
        required = []
        for name, (kind, parameter) in self.arguments.items():
            properties[name] = {"type": types[kind]}
            if parameter.default is inspect.Parameter.empty:
                required.append(name)
            else:
                properties[name]["default"] = parameter.default
        return {"type": "object", "properties": properties, "required": required,
                "additionalProperties": False}

    def validate(self, arguments):
        if set(arguments) - set(self.arguments):
            raise ValueError("unexpected argument")
        for name, (kind, parameter) in self.arguments.items():
            if name not in arguments:
                if parameter.default is inspect.Parameter.empty:
                    raise ValueError("required argument missing")
            elif not isinstance(arguments[name], kind):
                raise ValueError("argument has wrong type")


@dataclass
class Function:
    name: str
    description: str
    parameters: Parameters
    dependencies: dict
    run: object


class FunctionsRuntime:
    def __init__(self):
        self.functions = {}

    def register_function(self, function):
        dependencies = {}
        for name, hint in get_type_hints(function, include_extras=True).items():
            if get_origin(hint) is Annotated and isinstance(hint.__metadata__[0], Depends):
                dependencies[name] = hint.__metadata__[0]
        self.functions[function.__name__] = Function(
            function.__name__, inspect.getdoc(function), Parameters(function, dependencies),
            dependencies, function)

    def run_function(self, environment, name, kwargs, *, raise_on_error=False):
        try:
            function = self.functions[name]
            function.parameters.validate(kwargs)
            injected = {key: dependency.extract_dep_from_env(environment)
                        for key, dependency in function.dependencies.items()}
            return function.run(**kwargs, **injected), None
        except Exception as error:
            if raise_on_error:
                raise
            return "", type(error).__name__ + ": " + str(error)
