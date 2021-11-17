# exit immediately if virtualenv is not found
set -o errexit
set -o verbose

evergreen_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null 2>&1 && pwd)"
. "$evergreen_dir/prelude_python.sh"

python_loc=$(which ${python})
venv_dir="${workdir}/venv"
if [ -d "$venv_dir" ]; then
  exit 0
fi
"$python_loc" -m venv "$venv_dir"
echo "venv created"

# venv creates its Scripts/activate file with CLRF endings, which
# cygwin bash does not like. dos2unix it
# (See https://bugs.python.org/issue32451)
if [ "Windows_NT" = "$OS" ]; then
  dos2unix "${workdir}/venv/Scripts/activate"
fi

export VIRTUAL_ENV_DISABLE_PROMPT=yes


# the whole prelude cannot be imported because it requires pyyaml to be
# installed, which happens just below.
. "$evergreen_dir/activate_venv.sh"

activate_venv
echo "Upgrading pip to 21.0.1"
echo "Venv activated"

# ref: https://github.com/grpc/grpc/issues/25082#issuecomment-778392661
if [ "$(uname -m)" = "arm64" ] && [ "$(uname)" == "Darwin" ]; then
  export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
  export GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1
fi

python -m pip --disable-pip-version-check install "pip==21.0.1" "wheel==0.37.0" || exit 1
python -m pip install poetry
poetry install
echo "$(poetry --version)"

if [ $? != 0 ]; then
  echo "Pip install error"
  cat install.log
  exit 1
fi
