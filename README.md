# Example
```
from am_stl.stl.stl_parser import STLfile
from am_stl.stl.stl_builder import STLCreator

# Select an existing STL file
stl_file = STLfile(r"C:\Users\julianm\Documents\projects\am-geoalt\models\geoalt_architecture.stl")
# Load it, which returns a collection of all faces in the STL-file
face_collection = stl_file.load()

# Look for faces with overhang
face_collection.check_for_problems(ignore_grounded=True)
print(f'Found {len(face_collection.problem_faces)} problematic faces')
print(f'Found {len(face_collection.good_faces)} OK faces')

# Select where you want to save the STL file, and which face collection you want to use
stl_creator = STLCreator(r"./test.stl", face_collection)
# Build a new STL file
stl_creator.build_file()
```

