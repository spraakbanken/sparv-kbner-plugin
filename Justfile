default: test

# PYTHON = python

INVENV := if env_var_or_default('VIRTUAL_ENV', "") == "" { 'export VIRTUAL_ENV="${VENV_NAME}"; export PATH="${VENV_NAME}/bin:${PATH}"; unset PYTHON_HOME' } else { "" }

# ifeq (${VIRTUAL_ENV},)
#   VENV_NAME = .venv
#   INVENV = export VIRTUAL_ENV="${VENV_NAME}"; export PATH="${VENV_NAME}/bin:${PATH}"; unset PYTHON_HOME;
# else
#   VENV_NAME = ${VIRTUAL_ENV}
#   INVENV =
# endif
# ${info Using ${VENV_NAME}}

# venv: ${VENV_NAME}/.venv.created

# ${VENV_NAME}/.venv.created:
# 	test -d ${VENV_NAME} || ${PYTHON} -m venv ${VENV_NAME}
# 	${INVENV} pip install pip-tools
# 	@touch $@

test: dev
	{{INVENV}} pytest python/tests

test-release: dev-release
	{{INVENV}} pytest python/tests

dev:
	{{INVENV}} maturin develop

dev-release:
	{{INVENV}} maturin develop --release

# target/debug/libsparv_kbner.so: src/lib.rs
# 	${INVENV} maturin develop

# target/release/libsparv_kbner.so: src/lib.rs
# 	${INVENV} maturin develop --release
