# BlissScape Vote Party Notifier
Displays a desktop notification when a vote party is upcoming on BlissScape.

It cannot accurately keep track of the current number of votes due an inherent issue with how vote parties are implemented (meaning fixing it is beyond my reach). The issue is that the stats endpoint's votes are update live but the votes in-game (which are the ones that actually matter since they determine when the vote party starts) only update when players `::redeem` their votes. However, discrepancies in the vote count are rare since the typical behaviour of players is to redeem shortly after voting.

### Requirements
* Python 3.6 or higher
* `LINUX` Python DBUS bindings (see [here](https://ntfy.readthedocs.io/en/latest/#linux-desktop-notifications-linux))

### Installation
> `MACOS`: Desktop notifications will not work if ntfy is installed in a virtual environment. This also means pipenv cannot be used to install dependencies.

1. Download the [latest release](https://github.com/MarkKoz/vote-party-notifier/releases/latest)
2. Extract the contents of the archive
3. Open a terminal / command prompt
4. `cd` into the directory in which the archive was extracted
    ```bash
    cd path/to/vote-party-notifier
    ```
5. Install the dependencies

    If you're new to using pip, please read the [tutorial](https://packaging.python.org/tutorials/installing-packages/) on installing packages.

    > `NOTE`: It is highly recommended that dependencies are installed in either a [virtual environment](https://packaging.python.org/tutorials/installing-packages/#optionally-create-a-virtual-environment) or to the [user site](https://packaging.python.org/tutorials/installing-packages/#installing-to-the-user-site).

    Installation using pip and `requirements.txt`:
    ```bash
    pip3 install -r requirements.txt
    ```

    Alternatively, use pipenv to create a virtual environment and install the dependencies:
    ```bash
    pipenv sync
    ```

### Usage
Run the program as a module:

```bash
cd path/to/vote-party-notifier
python3 -m votepartynotifier --help
```

For now, to run it in the background, `nohup` can be used on UNIX systems and `pythonw` on Windows. A better solution is being considered for implementation in a future release.
