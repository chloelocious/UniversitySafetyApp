# UniversitySafety

## Installaton

We suggest you to create a virtual environment.

## 1. Create a Virtual Environment
Use Python's built-in `venv` module to create a virtual environment. Run the following command in the terminal:

```{sh}
python -m venv myenv
```

Here, myenv is the name of the virtual environment, and you can replace it with any name you prefer.

## 2. Activate the Virtual Environment
The method to activate the virtual environment depends on your operating system:

**Windows:**
```{sh}
myenv\Scripts\activate
```

**macOS/Linux:**

```{sh}
source myenv/bin/activate
```



## 3. Install Dependencies
Once activated, you can use pip to install all the dependencies needed

```{sh}
pip install -r requirements.txt
```
