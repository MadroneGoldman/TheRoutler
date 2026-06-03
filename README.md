<p align="center">
<pre style="color: green; font-weight: bold;">
 _____ _              __             _   _           
/__   \ |__   ___    /__\ ___  _   _| |_| | ___ _ __ 
  / /\/ '_ \ / _ \  / \/// _ \| | | | __| |/ _ \ '__|
 / /  | | | |  __/ / _  \ (_) | |_| | |_| |  __/ |   
 \/   |_| |_|\___| \/ \_/\___/ \__,_|\__|_|\___|_|   
    
</pre>
</p>

### Prerequisites

- Python >=3.14
- [uv](https://github.com/astral-sh/uv) package manager

### Installing uv
<details>
<summary>Details</summary>

##### follow the official directions at https://docs.astral.sh/uv/getting-started/installation/#standalone-installer
 or
```sh
# If you have pipx installed, this installs uv into an isolated environment
pipx install uv

# uv can also be installed this way
pip install uv

# if you use Homebrew on mac you can do
brew install uv
```
</details>

## Installation

Set your MBTA API key as an environment variable:

```sh
export MBTA_API_KEY=your_api_key_here
```

### Option 1: Run or install tool from Python wheel
<details>
<summary>Option 1A: Run tool without installing</summary>

##### To run tool from the wheel without explicitly installing into a persistent environment or adding it to your system's PATH.

- download wheel from [latest release](https://github.com/MadroneGoldman/TheRoutler/releases)

- Then run like this:
    ```sh
    uv tool run routler-0.1.0-py3-none-any.whl <command> <args>

    # You can also use `uvx` which is an alias for `uv tool run`
    uvx routler-0.1.0-py3-none-any.whl <command> <args>
    ```
</details>

<details>
<summary>Option 1B: Install tool</summary>

#####  To install the Python wheel persistently:

- download wheel from [latest release](https://github.com/MadroneGoldman/TheRoutler/releases)
- then install
    ```sh
        uv tool install routler-0.1.0-py3-none-any.whl
        # or
        pip install routler-0.1.0-py3-none-any.whl
        # or
        pipx install routler-0.1.0-py3-none-any.whl
    ```
- Now it can be run like:
    ```sh
    uv routler <command> <args>
    # or
    pip routler <command> <args>
    ```
</details>

## Usage

Run the CLI tool with command for the question you want to see:

```sh
routler question-one
routler question-two
routler question-three <first_stop> <second_stop>
```
*The command for question-three requires a first and second stop argument*
### Example

```sh
# To check question three's response for a trip from Ashmont to Arlington run:
routler question-three Ashmont Arlington

# Note: Stop names with spaces need to be surrounded with quotes
# so for a trip from Alewife to Science Park/West End do:
routler question-three Alewife "Science Park/West End"

#quotes around single word stop names are also accepted but not required:
routler question-three "Alewife" "Science Park/West End"
```

You can also run the tool with the "--help" flag to see a list of commands:

```sh
routler --help
```
Or add the "--help" flag to the end of a specific command for more info about that command specifically

```sh
routler question-one --help
```

## Development setup
1. Clone the repository and install dependencies:  
    ```sh
    git clone https://github.com/MadroneGoldman/TheRoutler.git
    cd routler
    uv sync
    ```

4. Get an API key from <https://api-v3.mbta.com>

3. Edit .env and add an api_key

4. Now you can run the tool like this
    ```sh
    uv run routler --help
    ```
    And run tests like this
    ```sh
    uv run pytest
    ```

*****

## Implementation notes
### Question one

My solution does the following:
1. Gets route data from the MBTA API for all “Light Rail” and “Heavy Rail" type routes
2. Add that data to a Pandas Dataframe with the columns:

    | Column Name | Description |
    | ----------- | ----------- |
    | long_name   | str: name of route (dataframe index) |
    | id          | str: MBTA api route id |
    | color       | str: hex color code |
3. Formats and prints the list of route "long_name"s from the datatable

Notes: 
*For question one I chose to filter the routes data with the api
*(https://api-v3.mbta.com/routes?filter[type]=0,1)* instead of downloading it all and filtering locally.*

*I don't see any benefit to filtering the data locally, it's just slower and more work.
You might want to filter it locally if you're aware of some bug or corner case with how the api classifes route types but for my purposes here the api is the source of truth.*

*Another reason you might want to filter the data locally is to extract some extra route data from that endpoint that could help with a path finding algorithm like in question three but in that case I would have the code for question 3 filter the routes locally and question one would still filter through the mbta api.*

### Question two

My solution does the following:
1. Runs the function from question one that returns a dataframe of subway routes

2. For each route in the dataframe use the route id to get it's stops from the mbta api endpoint : https://api-v3.mbta.com/stops?filter[route]={route id}

3. Consolidate the routes and stops into a Dataframe with the columns:
    | Column Name | Description                                              |
    | ----------- | -------------------------------------------------------- |
    | long_name   | str: name of route (dataframe index)                     |
    | id          | str: MBTA api route id                                   |
    | color       | str: hex color code (routes only, is None for stop rows) |
    | is_route    | bool: is element a route or stop                         |
    | links       | [str]: for routes - list of stop names along route        |
    |             | for stops - list of route names that use this stop        |
    | link_count  | int: length of links list                                |
4. With the dataframe created I can answer the 3 sub questions by applying filters
    1. links where is_route == true and link_count == max(link_count)
    2. links where is_route == true and link_count == min(link_count)
    3. links for rows where is_route == false and link_count > 1

Note: 
- *The routes endpoint has a param to include a 'stop' relationship but it only works when filtering routes by stop id
so it's less api calls to instead get stops from the stops endpoint filtered by route id*

### Question three

My solution does the following:
1. takes the first second stop as input from the user
2. uses the function from question two to get the dataframe of routes and stops
3. does a fuzzy search on the input stop names and list of stop names from the dataframe to ensure a valid match exists for both
4. Treats the dataframe as an adjaceny list and uses it to perform a breadth-first path search from the first stop to the second 
5. Print the path

Notes: 
- *There are lots of ways the pathfinding here could be made more efficent such as constructing an adjaceny matrix instead of an adjacency list*
- *And the graph representation of the subway system created here is very simple and doesn't take into account features such as: the direction of train lines and order of stops, or the physical location of stops and distances between them. Using more data availiable in the MBTA API like route patterns, route connections, and child stops a more sophisticated graph could be created which could output more efficent/useful routes between stops*
***

### ANSI color encoded route names:
<details>
<summary>Details</summary>
This tool utilizes the hex color code provided by the MBTA API per route to set the color of all route names output to the console.

A color in the 256 ANSI color space nearist to the hex color value from the MBTA api is found and the route name is encode in that color.
Unfortunatly most consoles dont support more than the standard 18 colors so for those consoles most or all route names will be output as standard white text. 
</details>

***
### General notes:
<details>
<summary>Details</summary>

- The project structure is seperated into 3 layer :
    - a cli layer (cli.py)
    - a middle "buisness logic" (subway_services.py)
    - and an MBTA API client/consumer layer (mbta_client.py) 

    But this is kind of overkill for such a small project and the middle layer could easily be merged into either of the other two layers
- The only tests that exist are some (very limited) unit tests for the middle layer. In a full project there should be more test coverage
- There's no logging in this project. The mbta_client.py logs when a http request retry occurs but thats it
- There's not much data validation or error handling some exceptions may be lost and not bubble up
- the mbta_client.py uses [aiohttp](https://docs.aiohttp.org/en/stable/index.html) to make asynchronous calls but the project never uses or benefits from that concurrency in any way. But it could be useful if the project was extended in some way.

</details>

***



























## Instructions for Dylan:

<details>
<summary>click if you're carberri</summary>

 ![Alt text]( https://tse1.mm.bing.net/th/id/OIP.xkcb-rjeUApIv2b3GG1KiQHaHa?rs=1&pid=ImgDetMain&o=7&rm=3)

1. install python https://www.python.org/downloads/
2. install uv https://docs.astral.sh/uv/getting-started/installation/#standalone-installer
3. download routler-0.1.0-py3-none-any.whl
 from https://github.com/MadroneGoldman/TheRoutler/releases/tag/DylanRelease
 4. open a terminal where you downladed the wheel and run routler like this:
 ```sh
uvx routler-0.1.0-py3-none-any.whl <command>

### commands are one of these
 question-one
 question-two
 question-three <first_stop> <second_stop>
 ```

</details>

 *****
