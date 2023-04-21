use std::borrow::BorrowMut;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyInt, PyList, PyString, PyTuple};

// #[pyclass]
// struct NerIterator {
//     tokens: Py<PyList>,
//     token_word: Py<PyList>,
//     sent: Py<PyList>,
//     sentence: Py<PyString>,
//     sent_index: usize,
//     curr_word_start: usize,
//     curr_token: usize,
// }

// impl NerIterator {
//     fn new(
//         tokens: Py<PyList>,
//         token_word: Py<PyList>,
//         sent: Py<PyList>,
//         sentence: Py<PyString>,
//     ) -> Self {
//         Self {
//             tokens,
//             token_word,
//             sent,
//             sentence,
//             sent_index: 0,
//             curr_word_start: 0,
//             curr_token: 0,
//         }
//     }
// }
// #[pymethods]
// impl NerIterator {
//     // fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
//     //     slf
//     // }
//     fn __next__(mut slf: PyRefMut<'_, Self>) -> IterNextOutput<PyTuple, ()> {
//         let sent = slf.sent.as_ref(slf.py());
//         if slf.sent_index >= sent.len() {
//             return IterNextOutput::Return(());
//         }
//         let curr_sent = sent.get_item(slf.sent_index);
//         println!("curr_sent = {:?}", curr_sent);
//         IterNextOutput::Return(())
//     }
// }

#[pyfunction]
fn interleave_tags_and_tokens(
    tokens: &PyList,
    token_word: &PyList,
    sent: &PyList,
) -> PyResult<Py<PyList>> {
    log::debug!("interleave_tags_and_tokens");
    Python::with_gil(|py| -> PyResult<Py<PyList>> {
        let list: Py<PyList> = PyList::empty(py).into();
        let mut curr_token = 0;
        if curr_token >= tokens.len() {
            return Ok(list);
        }
        let mut list_ref = list.as_ref(py);
        let tagged_tokens = list_ref.borrow_mut();
        let mut curr_word_start = 0usize;
        let mut token_start = tokens
            .get_item(curr_token)?
            .downcast::<PyDict>()?
            .get_item("start")
            .ok_or(PyRuntimeError::new_err("start is missing"))?
            .downcast::<PyInt>()?
            .extract::<usize>()?;
        log::info!("starting loop");
        for sent_val in sent.iter() {
            let curr_sent = sent_val.downcast::<PyInt>()?.extract::<usize>()?;
            let curr_word_end = curr_word_start
                + token_word
                    .get_item(curr_sent)?
                    .downcast::<PyString>()?
                    .len()?;
            if curr_word_start <= token_start && token_start < curr_word_end {
                let curr_token_ref = tokens.get_item(curr_token)?.downcast::<PyDict>()?;
                let entity = curr_token_ref
                    .get_item("entity")
                    .ok_or(PyRuntimeError::new_err("'entity' is missing"))?
                    .downcast::<PyString>()?
                    .extract::<&str>()?;
                let score_any = curr_token_ref
                    .get_item("score")
                    .ok_or(PyRuntimeError::new_err("'score' is missing"))?;
                // let score = score_any.downcast::<PyFloat>()?;
                // dbg!(&score);
                // let score = score.extract::<f32>()?;
                // dbg!(&score);
                tagged_tokens.append::<Py<PyTuple>>(
                    (curr_sent, translate_tag(entity), score_any.to_string()).into_py(py),
                )?;

                curr_token += 1;
                if curr_token >= tokens.len() {
                    println!("seen the last token, breaking...");
                    break;
                }
                token_start = tokens
                    .get_item(curr_token)?
                    .downcast::<PyDict>()?
                    .get_item("start")
                    .ok_or(PyRuntimeError::new_err("start is missing"))?
                    .downcast::<PyInt>()?
                    .extract::<usize>()?;
            }

            curr_word_start += token_word
                .get_item(curr_sent)?
                .downcast::<PyString>()?
                .len()?
                + 1;
        }
        Ok(list)
        // Py::new(py, NerIterator::new(tokens, token_word, sent, sentence))
    })
}

fn translate_tag(tag: &str) -> &str {
    if tag == "PER" {
        return "PRS";
    }
    tag
}
/// A Python module implemented in Rust.
#[pymodule]
fn sparv_kbner(_py: Python, m: &PyModule) -> PyResult<()> {
    pyo3_log::init();

    m.add_function(wrap_pyfunction!(interleave_tags_and_tokens, m)?)?;
    Ok(())
}
