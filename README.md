Code for our paper RED-Scenario: A Resource-Efficient Deployment Framework for Scenarios through Dependency Package Management
Code and partial explanations are provided, with more data and explanations to be organized and published after the paper is published.
# Abstract
The code contains the automated processes in the paper, as well as the associated assessments
# Usage
## Package-related test code
osv_download - Downloads OSV
osv_cve_build.py - Integrates specific files from OSV, used in experiments with npm and pypi

osv_pypi_product.py - Retrieves the Python versions that support vulnerabilities from osv_cve_build.json
osv_npm_product.py - Retrieves npm versions that support vulnerable packages from osv_cve_build.json

pypi_get_from_docker: Calls osv_pypi_product.py within Docker

node_dockerfile - Builds, installs, tests, and analyzes node packages
python_dockerfile - Builds, installs, tests, and analyzes python packages

osv_pypi_dockerfile and osv_npm_dockerfile.py - These two are for future work to test differences between all versions


## GitHub project-related code

### Data acquisition
github_high_star_get.py - Retrieves high-star projects
github_package_get.py - Retrieves node dependencies
github_requirement_get.py - Retrieves python dependencies



### Graphs
osv_pypi_size_require.py - Builds a Python seed graph
osv_pypi_size_requirelist.py - Builds a Python deep dependency graph
osv_npm_size_requie.py - Builds a node graph

graph_analys.py - Graph analysis

### Analysis of whether to apply merged package sizes
osv_node_one_size_analys.py
osv_node_multi_size_analys.py
osv_python_one_size_analys.py
osv_python_multi_size_analys.py

### Analysis of whether to apply merged application sizes
language_nodejs_files_size_gap.py
language_python_files_size_gap.py
language_python_files_size_gap_last.py
