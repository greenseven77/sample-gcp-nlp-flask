import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template
from io import BytesIO
import base64

@app.route('/plot')
def plot():
  img = BytesIO()
  y = [1,2,3,4,5]
  x = [0,2,1,3,4]

  plt.plot(x,y)
  plt.savefig(img, format='png')
  plt.close()
  img.seek(0)
  plot_url = base64.b64encode(img.getvalue()).decode('utf8')

  return render_template('plot.html', plot_url=plot_url)