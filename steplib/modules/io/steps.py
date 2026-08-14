"""IO step definitions for behave — files, JSON, and CSV operations."""

from __future__ import annotations

from typing import Any

from steplib.core.decorators import step
from steplib.core.registry import StepRegistry
from steplib.modules.io.actions import (
    io_append_file,
    io_assert_directory_exists,
    io_assert_directory_not_exists,
    io_assert_file_exists,
    io_assert_file_not_exists,
    io_assert_files_same,
    io_assert_json_matches_schema,
    io_assert_json_path_equals,
    io_assert_json_valid,
    io_assert_last_json_valid,
    io_close_csv_writer,
    io_copy_file,
    io_create_csv,
    io_create_csv_writer,
    io_create_directory,
    io_create_empty_file,
    io_create_json_path,
    io_delete_directory,
    io_delete_file,
    io_delete_json_path,
    io_diff_json_objects,
    io_get_file_extension,
    io_get_file_size,
    io_get_json_path_type,
    io_list_directory,
    io_load_json,
    io_merge_json,
    io_move_file,
    io_read_file,
    io_read_file_as_lines,
    io_rename_file,
    io_save_csv,
    io_save_json,
    io_set_csv_header_row,
    io_store_json_path,
    io_update_json_path,
    io_write_csv_row,
    io_write_file,
)
from steplib.modules.io.context import IOContext


def _get_io(context: Any) -> IOContext:
    """Get the IOContext from context.steplib, creating it if needed."""
    steplib = getattr(context, "steplib", None)
    if steplib is None:
        raise RuntimeError(
            "context.steplib is not initialized. "
            "Call autoload(context) or load(context, ...) in before_all."
        )
    io = getattr(steplib, "io", None)
    if io is None:
        io = IOContext()
        steplib.io = io
    return io


def _strip_quotes(value: str) -> str:
    """Strip surrounding quotes from a string argument."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


# ---------------------------------------------------------------------------
# File steps
# ---------------------------------------------------------------------------


@step(
    "I read the file {path} into {variable}",
    category="io",
    description="Read a file and store its content in a variable.",
    example='Given I read the file "data.txt" into "content"',
    i18n={
        "es": "Leo el archivo {path} en {variable}",
        "pt": "Eu leio o arquivo {path} em {variable}",
    },
)
def step_read_file(context: Any, path: str, variable: str) -> None:
    """Read a file into a variable."""
    io_read_file(_get_io(context), _strip_quotes(path), _strip_quotes(variable))


@step(
    "I write {content} to the file {path}",
    category="io",
    description="Write content to a file, overwriting if it exists.",
    example='Given I write "hello world" to the file "output.txt"',
    i18n={
        "es": "Escribo {content} en el archivo {path}",
        "pt": "Eu escrevo {content} no arquivo {path}",
    },
)
def step_write_file(context: Any, content: str, path: str) -> None:
    """Write content to a file."""
    io_write_file(_get_io(context), _strip_quotes(path), _strip_quotes(content))


@step(
    "I append {content} to the file {path}",
    category="io",
    description="Append content to a file, creating it if it does not exist.",
    example='Given I append "new line\\n" to the file "log.txt"',
    i18n={
        "es": "Añado {content} al archivo {path}",
        "pt": "Eu anexo {content} ao arquivo {path}",
    },
)
def step_append_file(context: Any, content: str, path: str) -> None:
    """Append content to a file."""
    io_append_file(_get_io(context), _strip_quotes(path), _strip_quotes(content))


@step(
    "I delete the file {path}",
    category="io",
    description="Delete a file.",
    example='Given I delete the file "temp.txt"',
    i18n={
        "es": "Elimino el archivo {path}",
        "pt": "Eu excluo o arquivo {path}",
    },
)
def step_delete_file(context: Any, path: str) -> None:
    """Delete a file."""
    io_delete_file(_get_io(context), _strip_quotes(path))


@step(
    "I copy the file {source} to {destination}",
    category="io",
    description="Copy a file from source to destination.",
    example='Given I copy the file "src.txt" to "dst.txt"',
    i18n={
        "es": "Copio el archivo {source} a {destination}",
        "pt": "Eu copio o arquivo {source} para {destination}",
    },
)
def step_copy_file(context: Any, source: str, destination: str) -> None:
    """Copy a file."""
    io_copy_file(_get_io(context), _strip_quotes(source), _strip_quotes(destination))


@step(
    "I move the file {source} to {destination}",
    category="io",
    description="Move a file from source to destination.",
    example='Given I move the file "old.txt" to "new.txt"',
    i18n={
        "es": "Muevo el archivo {source} a {destination}",
        "pt": "Eu movo o arquivo {source} para {destination}",
    },
)
def step_move_file(context: Any, source: str, destination: str) -> None:
    """Move a file."""
    io_move_file(_get_io(context), _strip_quotes(source), _strip_quotes(destination))


@step(
    "I rename the file {path} to {new_path}",
    category="io",
    description="Rename a file.",
    example='Given I rename the file "old.txt" to "new.txt"',
    i18n={
        "es": "Renombro el archivo {path} a {new_path}",
        "pt": "Eu renomeio o arquivo {path} para {new_path}",
    },
)
def step_rename_file(context: Any, path: str, new_path: str) -> None:
    """Rename a file."""
    io_rename_file(_get_io(context), _strip_quotes(path), _strip_quotes(new_path))


@step(
    "the file {path} exists",
    category="io",
    description="Assert that a file exists.",
    example='Then the file "output.txt" exists',
    i18n={
        "es": "el archivo {path} existe",
        "pt": "o arquivo {path} existe",
    },
)
def step_file_exists(context: Any, path: str) -> None:
    """Assert file exists."""
    io_assert_file_exists(_get_io(context), _strip_quotes(path))


@step(
    "the file {path} does not exist",
    category="io",
    description="Assert that a file does not exist.",
    example='Then the file "temp.txt" does not exist',
    i18n={
        "es": "el archivo {path} no existe",
        "pt": "o arquivo {path} não existe",
    },
)
def step_file_not_exists(context: Any, path: str) -> None:
    """Assert file does not exist."""
    io_assert_file_not_exists(_get_io(context), _strip_quotes(path))


@step(
    "the files {path1} and {path2} are the same",
    category="io",
    description="Assert that two files have the same content.",
    example='Then the files "a.txt" and "b.txt" are the same',
    i18n={
        "es": "los archivos {path1} y {path2} son iguales",
        "pt": "os arquivos {path1} e {path2} são iguais",
    },
)
def step_files_same(context: Any, path1: str, path2: str) -> None:
    """Assert two files have the same content."""
    io_assert_files_same(
        _get_io(context), _strip_quotes(path1), _strip_quotes(path2)
    )


@step(
    "I get the size of the file {path} as {variable}",
    category="io",
    description="Get the size of a file in bytes and store it in a variable.",
    example='Given I get the size of the file "data.bin" as "size"',
    i18n={
        "es": "Obtengo el tamaño del archivo {path} como {variable}",
        "pt": "Eu obtenho o tamanho do arquivo {path} como {variable}",
    },
)
def step_get_file_size(context: Any, path: str, variable: str) -> None:
    """Get file size into a variable."""
    io_get_file_size(
        _get_io(context), _strip_quotes(path), _strip_quotes(variable)
    )


@step(
    "I get the extension of the file {path} as {variable}",
    category="io",
    description="Get the extension of a file and store it in a variable.",
    example='Given I get the extension of the file "image.png" as "ext"',
    i18n={
        "es": "Obtengo la extensión del archivo {path} como {variable}",
        "pt": "Eu obtenho a extensão do arquivo {path} como {variable}",
    },
)
def step_get_file_extension(context: Any, path: str, variable: str) -> None:
    """Get file extension into a variable."""
    io_get_file_extension(
        _get_io(context), _strip_quotes(path), _strip_quotes(variable)
    )


@step(
    "I create an empty file at {path}",
    category="io",
    description="Create an empty file at the given path.",
    example='Given I create an empty file at "placeholder.txt"',
    i18n={
        "es": "Creo un archivo vacío en {path}",
        "pt": "Eu crio um arquivo vazio em {path}",
    },
)
def step_create_empty_file(context: Any, path: str) -> None:
    """Create an empty file."""
    io_create_empty_file(_get_io(context), _strip_quotes(path))


# ---------------------------------------------------------------------------
# JSON steps
# ---------------------------------------------------------------------------


@step(
    "I load the JSON file {path} as the last JSON",
    category="io",
    description="Load a JSON file and store it as the last JSON.",
    example='Given I load the JSON file "data.json"',
    i18n={
        "es": "Cargo el archivo JSON {path}",
        "pt": "Eu carrego o arquivo JSON {path}",
    },
)
def step_load_json(context: Any, path: str) -> None:
    """Load a JSON file."""
    io_load_json(_get_io(context), _strip_quotes(path))


@step(
    "I save the JSON to the file {path}",
    category="io",
    description="Save the last loaded JSON to a file.",
    example='Given I save the JSON to the file "output.json"',
    i18n={
        "es": "Guardo el JSON en el archivo {path}",
        "pt": "Eu salvo o JSON no arquivo {path}",
    },
)
def step_save_json(context: Any, path: str) -> None:
    """Save the last JSON to a file."""
    io_save_json(_get_io(context), _strip_quotes(path))


@step(
    "the JSON key path {key_path} equals {value}",
    category="io",
    description="Assert that a JSON key path equals a value.",
    example='Then the JSON key path "user.name" equals "Alice"',
    i18n={
        "es": "la ruta de clave JSON {key_path} es igual a {value}",
        "pt": "o caminho de chave JSON {key_path} é igual a {value}",
    },
)
def step_json_path_equals(context: Any, key_path: str, value: str) -> None:
    """Assert JSON key path equals value."""
    io_assert_json_path_equals(
        _get_io(context), _strip_quotes(key_path), _strip_quotes(value)
    )


@step(
    "I store the JSON key path {key_path} as {variable}",
    category="io",
    description="Extract a JSON key path value into a variable.",
    example='Given I store the JSON key path "user.id" as "user_id"',
    i18n={
        "es": "Guardo la ruta de clave JSON {key_path} como {variable}",
        "pt": "Eu armazeno o caminho de chave JSON {key_path} como {variable}",
    },
)
def step_store_json_path(context: Any, key_path: str, variable: str) -> None:
    """Store a JSON key path into a variable."""
    io_store_json_path(
        _get_io(context), _strip_quotes(key_path), _strip_quotes(variable)
    )


@step(
    "I update the JSON key path {key_path} to {value}",
    category="io",
    description="Update a JSON key path to a new value in-place.",
    example='Given I update the JSON key path "user.name" to "Bob"',
    i18n={
        "es": "Actualizo la ruta de clave JSON {key_path} a {value}",
        "pt": "Eu atualizo o caminho de chave JSON {key_path} para {value}",
    },
)
def step_update_json_path(context: Any, key_path: str, value: str) -> None:
    """Update a JSON key path value."""
    io_update_json_path(
        _get_io(context), _strip_quotes(key_path), _strip_quotes(value)
    )


@step(
    "I create the JSON key path {key_path} with value {value}",
    category="io",
    description="Create a nested JSON key path with a value.",
    example='Given I create the JSON key path "user.address.city" with value "Madrid"',
    i18n={
        "es": "Creo la ruta de clave JSON {key_path} con valor {value}",
        "pt": "Eu crio o caminho de chave JSON {key_path} com valor {value}",
    },
)
def step_create_json_path(context: Any, key_path: str, value: str) -> None:
    """Create a nested JSON key path."""
    io_create_json_path(
        _get_io(context), _strip_quotes(key_path), _strip_quotes(value)
    )


@step(
    "I delete the JSON key path {key_path}",
    category="io",
    description="Delete a JSON key path.",
    example='Given I delete the JSON key path "user.password"',
    i18n={
        "es": "Elimino la ruta de clave JSON {key_path}",
        "pt": "Eu excluo o caminho de chave JSON {key_path}",
    },
)
def step_delete_json_path(context: Any, key_path: str) -> None:
    """Delete a JSON key path."""
    io_delete_json_path(_get_io(context), _strip_quotes(key_path))


@step(
    "the JSON {json_string} is valid",
    category="io",
    description="Assert that a string is valid JSON.",
    example='Then the JSON \'{"key": "value"}\' is valid',
    i18n={
        "es": "el JSON {json_string} es válido",
        "pt": "o JSON {json_string} é válido",
    },
)
def step_json_valid(context: Any, json_string: str) -> None:
    """Assert a string is valid JSON."""
    io_assert_json_valid(_get_io(context), _strip_quotes(json_string))


@step(
    "the JSON matches the schema {schema_path}",
    category="io",
    description="Assert that the last loaded JSON matches a JSON Schema file.",
    example='Then the JSON matches the schema "schema.json"',
    i18n={
        "es": "el JSON coincide con el esquema {schema_path}",
        "pt": "o JSON corresponde ao esquema {schema_path}",
    },
)
def step_json_matches_schema(context: Any, schema_path: str) -> None:
    """Assert last JSON matches a schema."""
    io_assert_json_matches_schema(_get_io(context), _strip_quotes(schema_path))


@step(
    "the last JSON is valid",
    category="io",
    description="Assert that the last loaded JSON is valid by re-serializing it.",
    example='Then the last JSON is valid',
    i18n={
        "es": "el último JSON es válido",
        "pt": "o último JSON é válido",
    },
)
def step_last_json_valid(context: Any) -> None:
    """Assert the last loaded JSON is valid."""
    io_assert_last_json_valid(_get_io(context))


@step(
    "I get the type of the JSON key path {key_path} as {variable}",
    category="io",
    description="Get the type name of a JSON key path value.",
    example='Given I get the type of the JSON key path "user.age" as "age_type"',
    i18n={
        "es": "Obtengo el tipo de la ruta de clave JSON {key_path} como {variable}",
        "pt": "Eu obtenho o tipo do caminho de chave JSON {key_path} como {variable}",
    },
)
def step_get_json_path_type(context: Any, key_path: str, variable: str) -> None:
    """Get the type of a JSON key path value."""
    io_get_json_path_type(
        _get_io(context), _strip_quotes(key_path), _strip_quotes(variable)
    )


@step(
    "I diff the JSON objects {json1} and {json2}",
    category="io",
    description="Diff two JSON strings and assert no differences.",
    example='Then I diff the JSON objects \'{"a":1}\' and \'{"a":1}\'',
    i18n={
        "es": "Comparo los objetos JSON {json1} y {json2}",
        "pt": "Eu comparo os objetos JSON {json1} e {json2}",
    },
)
def step_diff_json(context: Any, json1: str, json2: str) -> None:
    """Diff two JSON objects."""
    result = io_diff_json_objects(
        _get_io(context), _strip_quotes(json1), _strip_quotes(json2)
    )
    if result["only_in_first"] or result["only_in_second"] or result["different"]:
        raise AssertionError(f"JSON objects differ: {result}")


@step(
    "I merge the JSON {origin_name} into {target_name} with {priority} priority",
    category="io",
    description="Merge two JSON dicts stored as variables.",
    example='Given I merge the JSON "defaults" into "config" with "origin" priority',
    i18n={
        "es": "Fusiono el JSON {origin_name} en {target_name} con prioridad {priority}",
        "pt": "Eu fundo o JSON {origin_name} em {target_name} com prioridade {priority}",
    },
)
def step_merge_json(
    context: Any, origin_name: str, target_name: str, priority: str
) -> None:
    """Merge two JSON dicts."""
    io_merge_json(
        _get_io(context),
        _strip_quotes(target_name),
        _strip_quotes(origin_name),
        _strip_quotes(priority),
    )


# ---------------------------------------------------------------------------
# CSV steps
# ---------------------------------------------------------------------------


@step(
    "I create the CSV file {path} from the data {data}",
    category="io",
    description="Create a CSV file from a JSON string representing a list of row dicts.",
    example='Given I create the CSV file "output.csv" from the data \'[{"a":1,"b":2}]\'',
    i18n={
        "es": "Creo el archivo CSV {path} con los datos {data}",
        "pt": "Eu crio o arquivo CSV {path} com os dados {data}",
    },
)
def step_create_csv(context: Any, path: str, data: str) -> None:
    """Create a CSV file from JSON data."""
    import json as _json

    try:
        rows = _json.loads(_strip_quotes(data))
    except _json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON data for CSV: {exc}") from exc
    io_create_csv(_get_io(context), _strip_quotes(path), rows)


@step(
    "I create a CSV writer for file {path} with fieldnames {fieldnames}",
    category="io",
    description="Create a CSV DictWriter and store it in the context.",
    example='Given I create a CSV writer for file "out.csv" with fieldnames "name,age"',
    i18n={
        "es": "Creo un escritor CSV para el archivo {path} con campos {fieldnames}",
        "pt": "Eu crio um escritor CSV para o arquivo {path} com campos {fieldnames}",
    },
)
def step_create_csv_writer(context: Any, path: str, fieldnames: str) -> None:
    """Create a CSV writer."""
    names = [f.strip() for f in _strip_quotes(fieldnames).split(",")]
    io_create_csv_writer(_get_io(context), _strip_quotes(path), names)


@step(
    "I write the CSV row {row}",
    category="io",
    description="Write a row to the active CSV writer.",
    example='Given I write the CSV row \'{"name":"Alice","age":30}\'',
    i18n={
        "es": "Escribo la fila CSV {row}",
        "pt": "Eu escrevo a linha CSV {row}",
    },
)
def step_write_csv_row(context: Any, row: str) -> None:
    """Write a row to the active CSV writer."""
    import json as _json

    try:
        data = _json.loads(_strip_quotes(row))
    except _json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON row for CSV: {exc}") from exc
    io_write_csv_row(_get_io(context), data)


@step(
    "I close the CSV writer",
    category="io",
    description="Close the active CSV writer and its file handle.",
    example='Then I close the CSV writer',
    i18n={
        "es": "Cierro el escritor CSV",
        "pt": "Eu fecho o escritor CSV",
    },
)
def step_close_csv_writer(context: Any) -> None:
    """Close the active CSV writer."""
    io_close_csv_writer(_get_io(context))


@step(
    "I save the CSV file",
    category="io",
    description="Flush the active CSV writer without closing it.",
    example='Then I save the CSV file',
    i18n={
        "es": "Guardo el archivo CSV",
        "pt": "Eu salvo o arquivo CSV",
    },
)
def step_save_csv(context: Any) -> None:
    """Flush the active CSV writer."""
    io_save_csv(_get_io(context))


@step(
    "I set the header row {row:d} for the CSV file {path} as {variable}",
    category="io",
    description="Read a CSV file using a specific row as the header and store rows in a variable.",
    example='Given I set the header row 2 for the CSV file "data.csv" as "rows"',
    i18n={
        "es": "Establezco la fila de cabecera {row:d} para el archivo CSV {path} como {variable}",
        "pt": "Eu defino a linha de cabeçalho {row:d} para o arquivo CSV {path} como {variable}",
    },
)
def step_set_csv_header_row(context: Any, row: int, path: str, variable: str) -> None:
    """Set the header row for a CSV file."""
    io_set_csv_header_row(
        _get_io(context), _strip_quotes(path), row, _strip_quotes(variable)
    )


# ---------------------------------------------------------------------------
# Directory steps
# ---------------------------------------------------------------------------


@step(
    "I create the directory {path}",
    category="io",
    description="Create a directory, including parents if needed.",
    example='Given I create the directory "output/logs"',
    i18n={
        "es": "Creo el directorio {path}",
        "pt": "Eu crio o diretório {path}",
    },
)
def step_create_directory(context: Any, path: str) -> None:
    """Create a directory."""
    io_create_directory(_strip_quotes(path))


@step(
    "the directory {path} exists",
    category="io",
    description="Assert that a directory exists.",
    example='Then the directory "output" exists',
    i18n={
        "es": "el directorio {path} existe",
        "pt": "o diretório {path} existe",
    },
)
def step_directory_exists(context: Any, path: str) -> None:
    """Assert directory exists."""
    io_assert_directory_exists(_strip_quotes(path))


@step(
    "the directory {path} does not exist",
    category="io",
    description="Assert that a directory does not exist.",
    example='Then the directory "temp" does not exist',
    i18n={
        "es": "el directorio {path} no existe",
        "pt": "o diretório {path} não existe",
    },
)
def step_directory_not_exists(context: Any, path: str) -> None:
    """Assert directory does not exist."""
    io_assert_directory_not_exists(_strip_quotes(path))


@step(
    "I list the files in the directory {path} as {variable}",
    category="io",
    description="List files in a directory and store them as a variable.",
    example='Then I list the files in the directory "data" as "files"',
    i18n={
        "es": "Listo los archivos del directorio {path} como {variable}",
        "pt": "Eu listo os arquivos do diretório {path} como {variable}",
    },
)
def step_list_directory(context: Any, path: str, variable: str) -> None:
    """List directory contents."""
    io_list_directory(_get_io(context), _strip_quotes(path), _strip_quotes(variable))


@step(
    "I delete the directory {path}",
    category="io",
    description="Delete a directory and all its contents.",
    example='When I delete the directory "temp"',
    i18n={
        "es": "Elimino el directorio {path}",
        "pt": "Eu excluo o diretório {path}",
    },
)
def step_delete_directory(context: Any, path: str) -> None:
    """Delete a directory."""
    io_delete_directory(_strip_quotes(path))


@step(
    "I read the file {path} as lines into {variable}",
    category="io",
    description="Read a file and store its lines as a list in a variable.",
    example='Given I read the file "data.txt" as lines into "lines"',
    i18n={
        "es": "Leo el archivo {path} como líneas en {variable}",
        "pt": "Eu leio o arquivo {path} como linhas em {variable}",
    },
)
def step_read_file_as_lines(context: Any, path: str, variable: str) -> None:
    """Read file as lines."""
    io_read_file_as_lines(
        _get_io(context), _strip_quotes(path), _strip_quotes(variable)
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

_ALL_STEPS = [
    # File
    step_read_file,
    step_write_file,
    step_append_file,
    step_delete_file,
    step_copy_file,
    step_move_file,
    step_rename_file,
    step_file_exists,
    step_file_not_exists,
    step_files_same,
    step_get_file_size,
    step_get_file_extension,
    step_create_empty_file,
    # Directory
    step_create_directory,
    step_directory_exists,
    step_directory_not_exists,
    step_list_directory,
    step_delete_directory,
    step_read_file_as_lines,
    # JSON
    step_load_json,
    step_save_json,
    step_json_path_equals,
    step_store_json_path,
    step_update_json_path,
    step_create_json_path,
    step_delete_json_path,
    step_json_valid,
    step_json_matches_schema,
    step_last_json_valid,
    step_get_json_path_type,
    step_diff_json,
    step_merge_json,
    # CSV
    step_create_csv,
    step_create_csv_writer,
    step_write_csv_row,
    step_save_csv,
    step_set_csv_header_row,
    step_close_csv_writer,
]


def register(registry: StepRegistry) -> None:
    """Register all io steps into the given registry."""
    for step_fn in _ALL_STEPS:
        registry.add(step_fn)
