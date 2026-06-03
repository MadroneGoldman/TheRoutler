# AgZen Take Home Challenge

## Intro

## Usage

Run the CLI tool with command for the question you want to see:

```sh
routler question-one
routler question-two
routler question-three <first_stop> <second_stop>
```
The command for question-three requires a first and second stop argument
### Example

To check question threes response for a trip from Ashmont to Arlington run:

```sh
routler question-three Ashmont Arlington
```

You can also run the tool with the "--help" flag to see a list of commands:

```sh
routler --help
```
Or add the "--help" flag to the end of a specific command for more info about that command specifically

```sh
routler question-one --help
```
Run the CLI tool with the "--help" argument to see a list of commands:

## Installation

### Prerequisites

- Python >=3.14
- [uv](https://github.com/astral-sh/uv) package manager

### Installing uv
##### follow the official directions at https://docs.astral.sh/uv/getting-started/installation/#standalone-installer
 or
```sh
# Assuming you have pipx installed, this is the recommended way since it installs
# uv into an isolated environment
pipx install uv

# uv can also be installed this way
pip install uv

# if you use Homebrew on mac you can do
brew install uv
```
### Run or install tool from Python wheel (.whl)

1. Run tool from the wheel without explicitly installing into a persistent environment or adding it to our system's PATH.

```sh
uv tool run routler-0.1.0-py3-none-any.whl

# You can also use `uvx` which is an alias for `uv tool run`
uvx routler-0.1.0-py3-none-any.whl
```
1. Install the Python wheel persistently:

```sh
uv tool install routler-0.1.0-py3-none-any.whl
# or
pip install routler-0.1.0-py3-none-any.whl
# or
pipx install routler-0.1.0-py3-none-any.whl
```

### Building from source
1. Clone the repository:

```sh
git clone https://github.com/<>.git
cd project_name
```

1. Build using uv:

```sh
uv build
```

1. Test the Python wheel created during the build step:

```sh
uv tool run routler-0.1.0-py3-none-any.whl

# You can also use `uvx` which is an alias for `uv tool run`
uvx routler-0.1.0-py3-none-any.whl
```


## Implementation notes


## Running tests