# alpacas-cli

Command Line Interface for the Alpaca API written in Python designed for managing portfolios via simple commands, running algorithmic analyses and building on top of it.

## 🔧 Setting Up the Development Environment

To get started with the project, it's recommended to use a virtual environment to manage dependencies. Follow the steps below:

### 1. Clone the Repository

```bash
git clone https://github.com/leonroberts/alpacas-cli.git
cd alpacas-cli
```

### 2. Create a Virtual Environment

**On MacOs/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```
**On Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### (Rapid Setup) 

If you want to quickly set up the project, use the provided scripts:

***MacOS/Linux:**

```bash
bash rapid_setup.sh
```

**Windows:**

```bash
.\rapid_setup.bat
```

## 📝 Usage

To use the CLI, run the following command while the virtual environment is activated:

```bash
python .\alpacas-cli\main.py
```

### First Login Session

In the first login session, you will be prompted to enter the name of your portfolio, your Alpaca API key, and secret key. This information is stored in a configuration file located at `configs/alpaca.json` and is necessary for the CLI to interact with the Alpaca API.

**If you do not have an Alpaca account, you can sign up at [Alpaca](https://alpaca.markets/), it is for FREE.**

### First Steps

After the first loggin session, you can start using the CLI to manage your portfolio. Using the command `help` will show you all available commands and their descriptions.

```bash
>>> help
================================================================================
                              Command Information
================================================================================
  add_tickers   Adds a custom collection of tickers to the configuration file.
  alias         Manage command aliases/shortcuts
  analysis      Run various analyses on the portfolio
  banner        Displays the application banner with version and author information.
  clear         Clears the terminal screen.
  exchanges     Displays the current status of major stock exchanges.
  exit          Exits the program.
  help          Displays information about available commands.
  info          Displays information about available commands.
  init          Initializes a new portfolio with user-provided details.
  list          Lists all available portfolios, highlighting the currently loaded one.
  list_tickers  Lists all available ticker sets from the configuration file.
  load          Loads an existing portfolio from storage. Requires no active portfolio.
  load_last     Loads the most recently used portfolio.
  overview      Prints the portfolio overview.
  performance   Displays the historical portfolio performance using Alpaca's API.
  trade_asset   Places a buy, sell, or short order for a specified asset using the Alpaca
                API.
  trade_crypto  Places a buy or sell order for a cryptocurrency using the Alpaca Crypto API.
  unload        Unloads the currently active portfolio.
================================================================================
```

With alpaca it is possible to manage multiple portfolios. Actions on specific portolios can be performed by using the `load` command. The interface will ask you to select a portfolio. The active portfolio will be added to the CLI entry prompt.

```bash	
>>> load
Enter the name of the portfolio: Getting Started 

Getting Started >>>
```

You can look at the positions of the portfolio by using the `overview` command.

```bash
>>> overview
```

Or evaluate your portfolio's performance with the `performance` command.

```bash
>>> performance
```

Of course, it is possible to trade assets in your portfolio. Use the `trade_asset` command to buy, sell or short an asset.

```bash
>>> trade_asset
```

The CLI will prompt you with the necessary information to place an order. 

**Analyses** can be run using the `analysis` command. However, this requires for you to build a custom analysis first that suits your needs. The code for a sample analysis can be found in `alpacas-cli/analysis/analysis.py`. 

To check the status of all analyses, first use the `analysis` command and then select `status`. Analysis can run in the background however, when ending the CLI, all analyses will be stopped. To stop a specific analysis, use the `stop <id>` command. The ID can be found in the status output.

## 🛠️ Development

The best part about this project is that it is designed to be easily extensible. You can add new commands, analyses, or features by following the existing patterns in the codebase.

**Always make sure to follow the distribution guidelines, document your code and run the tests.**

## Goals

In the following list you will find some goals, that I think would be cool to achieve for this tool. I am happy to discuss about this prioritize other ideas in the development and integration process:
- [ ] Build a dev community that likes the idea of the project and is eager to spend some more time on the development 
- [ ] Build a foundation of common analyses from the quant world
- [ ] Integrate dedicated portfolio optimazation packages, like [PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt/tree/master)

## Support

The best support would be given by co-developing, finding errors in the code or writing down more detailed documentation.
