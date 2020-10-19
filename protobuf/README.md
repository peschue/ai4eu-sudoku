We have 4 protobuf files.

3 protobuf files for components.
1 protobuf file for the orchestrator.

We only need the orchestrator protobuf file, because otherwise we will get name clashes because certain classes are defined in multiple compilation units.
The orchestrator file contains all definitions of all components, but each definition only once.