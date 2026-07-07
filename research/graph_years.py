import matplotlib.pyplot as plt
import numpy as np
import json
from matplotlib.ticker import MaxNLocator

large = 'Database/seasons_large.json'
LARGE: dict
with open(large, 'r') as file:
    LARGE = json.load(file)


def print_time(days):
    hour = (days-int(days))*24
    minute = (hour-int(hour))*60
    seconds = (minute-int(minute))*60
    return f'{int(days)} days - {int(hour)}h {int(minute)}m {int(seconds)}s'


COLOR = ['#FFEE00', '#8E55B9', '#0073E6', '#00B500', '#FFAA00', '#FF0000']
Seasons = dict()
Seasons['Light Season'] = []
Seasons['Dark Season'] = []
Seasons['Winter'] = []
Seasons['Spring'] = []
Seasons['Summer'] = []
Seasons['Autumn'] = []

Seasons['Year'] = []

for k, v in LARGE.items():
    if int(k) < 17190:
        Seasons['Light Season'].append(v['Spring']['duration']+v['Summer']['duration'])
        Seasons['Dark Season'].append(v['Autumn']['duration'] +
                               LARGE[str(int(k)+1)]['Winter']['duration'])
    else:
        Seasons['Light Season'].append(Seasons['Light Season'][-1])
        Seasons['Dark Season'].append(Seasons['Dark Season'][-1])
    Seasons['Winter'].append(v['Winter']['duration'])
    Seasons['Spring'].append(v['Spring']['duration'])
    Seasons['Summer'].append(v['Summer']['duration'])
    Seasons['Autumn'].append(v['Autumn']['duration'])
    Seasons['Year'].append(v['duration'])

seconds = sum(Seasons['Year'])/len(Seasons['Year'])
avgYear = print_time(seconds/86400)
avgSeason = print_time(seconds/(4*86400))
avgHalf = print_time(seconds/(2*86400))


def singleY_graph(what=['Year']):
    X = []
    for k in LARGE.keys():
        X.append(int(k))

    for i, (k, v) in enumerate(Seasons.items()):
        if k in what:
            Y = [i for i in v]
            average = np.mean(Y)

            if k == 'Year':
                unit = 'MINUTES'
                Y = [(i-average)/60 for i in Y]
                average = (seconds-average)/60
            else:
                avgSpecificSeason = print_time((sum(Y)/len(Y))/86400)
                unit = 'HOURS'
                Y = [(i-average)/3600 for i in Y]
                if k in ['Light Season', 'Dark Season']:
                    average = (seconds/2-average)/3600
                else:
                    average = (seconds/4-average)/3600

            # Kreiranje grafika
            plt.figure(figsize=(10, 6), num=f'Single Graph {k}')
            # Prikaz podataka
            if k == 'Year':
                plt.plot(X, Y, label=f"Deviation ({unit})", color='blue')
            else:
                plt.plot(X, Y, label=f"Deviation ({unit})", color=COLOR[i])
            plt.plot(X, [average] * len(X), color='silver', linestyle='-')

            plt.gca().xaxis.set_major_locator(
                MaxNLocator(integer=True, prune='lower', nbins=34))
            for x_val in [i for i in range(-13000,17001,1000)]:
                plt.gca().axvline(x=x_val, color='silver', linestyle='--', alpha=0.6)
            plt.gca().yaxis.set_major_locator(
                MaxNLocator(integer=True, prune='lower', nbins=20))

            # Postavke grafika
            period = 'Mean Year' if k == 'Year' else 'Mean Quarter of Year' if k not in [
                'Light Season', 'Dark Season'] else 'Mean Half of Year'

            TITLE = f"Changes in duration of Astronomical {k}"
            TITLE += f"{' Period' if k in ['Light Season', 'Dark Season'] else ''}{'' if k == 'Year' else ' on Northern Hemisphere'}\n"
            TITLE += f"{period}: {avgYear if k == 'Year' else avgSpecificSeason}"

            plt.title(TITLE, fontsize=16)
            plt.xlabel(f"Year", fontsize=14)
            plt.ylabel(f"Deviation from {period} in {unit}", fontsize=14)
            plt.xlim(min(X), max(X))
            plt.ylim(min(Y)+min(Y)*0.01, max(Y)+max(Y)*0.01)

            plt.tight_layout()


def multiY_graph(what=['Light Season', 'Dark Season', 'Summer', 'Autumn', 'Spring', 'Winter']):
    plt.figure(figsize=(10, 6), num=f'Multi Graph {' '.join(what)}')

    X = [int(k) for k in LARGE.keys()]
    SEASONS = list(Seasons.keys())[:-1]
    season = dict()
    periods = [k for k in SEASONS if k in what]

    for k in periods:
        season[k] = [i/3600 for i in Seasons[k]]

    Y = []

    for k in season.keys():
        if k in ['Light Season', 'Dark Season']:
            season[k] = [i - seconds/(2*3600) for i in season[k]]
        else:
            season[k] = [i - seconds/(4*3600) for i in season[k]]
        Y += season[k]

    average = np.mean(Y)

    for part in periods:
        i = SEASONS.index(part)
        plt.plot(X, season[part], label=part, color=COLOR[i])

    plt.axhline(y=average, color='silver', linestyle='-',
                label=f"Average: {average:.0f} hours")

    # Podesite osovinu i postavke grafikona
    plt.gca().xaxis.set_major_locator(
        MaxNLocator(integer=True, prune='lower', nbins=34))
    for x_val in [i for i in range(-13000,17001,1000)]:
        plt.gca().axvline(x=x_val, color='silver', linestyle='--', alpha=0.6)
    plt.gca().yaxis.set_major_locator(
        MaxNLocator(integer=True, prune='lower', nbins=20))

    # Postavke grafika
    TITLE = f"Changes in duration of Astronomical Seasons on Northern Hemisphere\n"
    TITLE += f"Mean Quarter of the Year: {avgSeason}\n"
    TITLE += f"Mean Half of the Year: {avgHalf}"
    plt.title(TITLE, fontsize=16)
    plt.xlabel("Year", fontsize=14)
    plt.ylabel(f"Deviation from mean Quarter/Half Year in HOURS", fontsize=14)
    plt.xlim(min(X), max(X))
    plt.ylim(min(Y)+min(Y)*0.01, max(Y)+max(Y)*0.01)

    plt.legend()
    plt.tight_layout()


#multiY_graph(['Light Season', 'Dark Season'])  # 1 Graph
#multiY_graph(['Summer', 'Winter'])  # 1 Graph
#multiY_graph(['Autumn', 'Spring'])  # 1 Graph
#multiY_graph(['Summer', 'Autumn', 'Spring', 'Winter'])  # 1 Graph
multiY_graph(['Light Season', 'Dark Season', 'Summer', 'Autumn',
             'Spring', 'Winter'])  # 1 Graph
#singleY_graph(['Summer', 'Autumn', 'Spring', 'Winter'])  # 4 Graph
#singleY_graph(['Light Season', 'Dark Season'])  # 2 Graph
singleY_graph(['Year'])  # 1 Graph
plt.show()

# -4080 : 6430 : 16500
# -9600 : 950 : 10900