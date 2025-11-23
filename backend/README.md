# Require : Python 3.12

# Setup commands

```bash
pip install uv
uv sync
```

# Install fastText 176 language model

```bash
mkdir -p src/lang_detect
wget -O src/lang_detect/lid.176.ftz https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz
```


Testing 

```python
python -m unittest backend/tests/test_lang_detect.py
```
