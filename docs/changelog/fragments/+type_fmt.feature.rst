Improve formatting types inside generics for error messages

.. parsed-literal::

  adaptix.ProviderNotFoundError: Cannot produce dumper for type <class '__main__.Foo'>
  × Cannot create dumper for model. Dumpers for some fields cannot be created
  │ Location: ‹Foo›
  ╰──▷ Cannot create dumper for model. Dumpers for some fields cannot be created
     │ Location: ‹Foo.limit: __main__.MinMax[__main__.Bar]›
     ├──▷ Cannot create dumper for union. Dumpers for some union cases cannot be created
     │  │ Location: ‹__main__.MinMax[__main__.Bar].min: Optional[__main__.Bar]›
     │  ╰──▷ Cannot find dumper
     │       Location: ‹Bar›
     ╰──▷ Cannot create dumper for union. Dumpers for some union cases cannot be created
        │ Location: ‹__main__.MinMax[__main__.Bar].max: Optional[__main__.Bar]›
        ╰──▷ Cannot find dumper
             Location: ‹Bar›


.. parsed-literal::

  adaptix.ProviderNotFoundError: Cannot produce dumper for type <class '__main__.Foo'>
    × Cannot create dumper for model. Dumpers for some fields cannot be created
    │ Location: ‹Foo›
    ╰──▷ Cannot create dumper for model. Dumpers for some fields cannot be created
       │ Location: ‹Foo.limit: MinMax[Bar]›
       ├──▷ Cannot create dumper for union. Dumpers for some union cases cannot be created
       │  │ Location: ‹MinMax[Bar].min: Optional[Bar]›
       │  ╰──▷ Cannot find dumper
       │       Location: ‹Bar›
       ╰──▷ Cannot create dumper for union. Dumpers for some union cases cannot be created
          │ Location: ‹MinMax[Bar].max: Optional[Bar]›
          ╰──▷ Cannot find dumper
               Location: ‹Bar›
