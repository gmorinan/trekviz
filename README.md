## TREKVIZ

Dashboard used to visualise how many lines and interactions characters have in the different Star Trek series.

To run this locally:
```
streamlit run app.py
```

Main libraries used are: [Streamlit](https://streamlit.io/), [Altair](https://altair-viz.github.io/), [Networkx](https://networkx.org/) & [Pyvis](https://pyvis.readthedocs.io/en/latest/)



#### NOTES 
* Interactions = the number of consecutive lines the two characters shared.
* Transcripts of episodes were used, hence "Episode Number" is actually transcript number.
* Some transcripts covered 2-parters, hence why there are less transcripts that aired episodes.
* Recent series (Discovery, Picard, Lower Decks) are not included due to lack of online transcripts. 


## ABOUT

Author: [@gmorinan](https://www.linkedin.com/in/gmorinan/) ([source code](https://github.com/gmorinan/trekviz))

Data source: [chakoteya.net](http://www.chakoteya.net/)

StarTrek rights owner: [ViacomCBS](https://www.viacomcbs.com/)




