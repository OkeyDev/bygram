# Instruction 

First of all - definition of builtin types. We should skip it:
```
double ? = Double;  # It's unique style, so we just ignore it
string ? = String;

int32 = Int32;
int53 = Int53;
int64 = Int64;
bytes = Bytes;

boolFalse = Bool;
boolTrue = Bool;

vector {t:Type} # [ t ] = Vector t;
```

## definition types

#### Multiline definition
```
//@description An object of this type can be returned on every function call, in case of an error
//@code Error code; subject to future changes. If the error code is 406, the error message must not be processed in any way and must not be displayed to the user
//@message Error message; subject to future changes
error code:int32 message:string = Error;
```


#### Inline definition
```
//@class AuthenticationCodeType @description Provides information about the method by which an authentication code is delivered to the user
```

There is comment with @class definition and description;

### Class definition
That rules are applied for multiline and inline definitions.

```
authenticationCodeTypeTelegramMessage length:int32 = AuthenticationCodeType;
```
class authenticationCodeTypeTelegramMessage inhearted from AuthenticationCodeType.

```
error code:int32 message:string = Error;
```
Name is the same as parent (diff case, but it's ok). So it's independent class and not inhearted from anything.

```
//@class AuthenticationCodeType @description Provides information about the method by which an authentication code is delivered to the user
```
Same. It's independent class. 


## Functions 
All functions have the same definition type but it all after row ---functions---
