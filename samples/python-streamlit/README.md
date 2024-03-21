## CPU Power Curve using Python with Streamlit
Sample created to help understanding

Benchmarks: 
- [Psutil](https://pypi.org/project/psutil/) 
- NGINX using [WRK](https://github.com/wg/wrk)


How to test:
```bash
$ streamlit run greenchips.py
```

debug mode:
```bash
streamlit run greenchips.py --logger.level=debug 3
```

### screens

<p align="center"><img src="images/image.png" width=800px height=400px></p>

<p align="center"><img src="images/image-1.png" width=800px height=400px></p>

<p align="center"><img src="images/image-2.png" width=800px height=400px></p>


### Tests with Turbostress
CPU Info:
```
CPU Count: 8
Total Cores: 16
CPU Frequency: 4475.9260625
```

<p align="center"><img src="images/image-3.png" width=600px height=400px></p>


