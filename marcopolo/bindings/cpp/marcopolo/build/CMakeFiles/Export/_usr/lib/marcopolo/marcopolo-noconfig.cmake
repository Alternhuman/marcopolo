#----------------------------------------------------------------
# Generated CMake target import file for configuration "".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "marcopolo_marcopolo" for configuration ""
set_property(TARGET marcopolo_marcopolo APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(marcopolo_marcopolo PROPERTIES
  IMPORTED_LOCATION_NOCONFIG "/usr/lib/libmarcopolo.so"
  IMPORTED_SONAME_NOCONFIG "libmarcopolo.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS marcopolo_marcopolo )
list(APPEND _IMPORT_CHECK_FILES_FOR_marcopolo_marcopolo "/usr/lib/libmarcopolo.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
