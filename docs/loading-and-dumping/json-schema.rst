==================
JSON Schema
==================


Calling generation
========================

Introduction
-------------------

A JSON Schema can be generated from any type supported by |adaptix|.
It describes the structure of data produced by the dumper, as well as the valid structure expected by the loader.

.. literalinclude:: /examples/loading-and-dumping/json_schema/introduction.py

:func:`.generate_json_schema` takes retort object,
so generated JSON Schema is synchronized with actual configured behaviour.

There are two directions of JSON Schema. :py:attr:`.Direction.INPUT` refers to schema of loader,
while :py:attr:`.Direction.OUTPUT` means schema of dumper.
The schema should look different for the same type, depending on whether it’s used for parsing or for dumping.

.. dropdown:: Output schema example

   .. literalinclude:: /examples/loading-and-dumping/json_schema/introduction_output.py

   Field ``tags`` become required and ``additionalProperties`` attribute is gone.


Multi-model schemas
------------------------

The example above shows how to generate a JSON schema for a single type.
However, Adaptix can also generate JSON schemas for multiple types at once,
producing a consistent description for an entire group of types.

To do this, use the :func:`.generate_json_schemas_namespace`.

.. literalinclude:: /examples/loading-and-dumping/json_schema/generate_json_schemas_namespace.py

Identical schemas with same ref are merged together.
If different schemas share the same ref, those refs are mangled to avoid ambiguity.
The process of building a consistent schema is quite sophisticated and takes many subtle factors into account
— it will be covered in more detail in the following sections.

Common customization
========================


Overriding schema with custom loader/dumper
------------------------------------------------

When you declare a new loader or dumper for a type, the previously associated schema is erased.
This design ensures that users who require JSON Schema generation
explicitly specify how the schema should change along with the new function,
keeping it tightly synchronized with the actual runtime behavior.

The :func:`.loader` and :func:`.dumper` functions have a ``json_schema`` parameter
that lets you define a new schema for the given predicate.

Possible values:

- :class:`.EraseJSONSchema` — disables schema generation for this predicate (default).
- :class:`.KeepJSONSchema` — preserves the previously defined schema for this predicate.
  If the previous schema was erased, the new one will also be considered erased.
  To redefine the schema, use one of the following options.
- :class:`.JSONSchema` — defines a new schema value for this predicate.
- :class:`.JSONSchemaPatch` — modifies the existing schema for this predicate.
  This will be covered in more detail in the next section.

You can create a :class:`.JSONSchema` instance directly.
This class follows PEP8 naming conventions: for example, ``$ref`` becomes ``ref``, and ``anyOf`` becomes ``any_of``.
However, if you prefer to use the original JSON terminology,
you can also construct an instance directly from a raw JSON definition using :func:`.load_json_schema`.

Overriding only schema
------------------------------------------------

The :func:`.json_schema` function is used for various kinds of JSON Schema customization in |adaptix|.
This functionality will be discussed in more detail in later sections.
For now, note that you can override the schema
for specific types in exactly the same way as with :func:`.loader` and :func:`.dumper`.

Patching existing schema
---------------------------

To modify an already generated JSON schema, you can use the :class:`.JSONSchemaPatch` class.

.. literalinclude:: /examples/loading-and-dumping/json_schema/patching_merge_with.py

:meth:`.JSONSchemaPatch.merge_with`

:meth:`.JSONSchemaPatch.replace`

:meth:`.JSONSchemaPatch.mutate_copy`

:meth:`.JSONSchemaPatch.mutate_deepcopy`


Reference pinning
---------------------------

|Adaptix| automatically generates programmatic identifiers for all types.
By default, it uses the type’s name, but if name collisions occur, the fully qualified name (``__qualname__``) is used instead.

If two different schemas happen to share the same ``__qualname__``
— for example, when using field-name-based predicates — Adaptix distinguishes them via counter.

.. custom-non-guaranteed-behavior::

  Reference stability between releases or after code changes is not guaranteed.
  To ensure stable type references, you should explicitly specify the reference for a type using :paramref:`.json_schema.ref`.

If two different schemas are assigned the same fixed reference, |adaptix| will raise an error.
All automatically generated references are mangled as needed to avoid conflicts with explicitly pinned ones.


Schema inlining
---------------------------


Deep customization
========================


Glancing inside
---------------------------


Name mangling
---------------------------


Reference generation
---------------------------


Integrating into common schema namespace
------------------------------------------


Trash
---------


.. hint::

  This means that the default schema generator does not account for any implicit coercion the loader might perform.

