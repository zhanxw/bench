from distutils.core import setup
setup(
    name = "bench",
    scripts = ['scripts/monitor.py'],
    requires = ['psutil', 'pandas', 'numpy'],
    version = "2.7",
    description = "Benchmark resources usage",
    author = "Xiaowei Zhan",
    author_email = "zhanxw@gmail.com",
    url = "http://zhanxw.com/bench",
    download_url = "https://pypi.python.org/pypi/bench",
    keywords = ["benchmark", "process", "monitor"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Monitoring",
        ],
    long_description = open('README.txt').read()
)
