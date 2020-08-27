#-*- coding: utf-8 -*-


from datetime import datetime
from dateutil import relativedelta

def calcult_date(date_debut="28/05/2016", date_fin="14/06/2021"):
	#print('on est dedans')
	date_debut = datetime.strptime(date_debut, '%Y-%m-%d')
	date_fin = datetime.strptime(date_fin, '%Y-%m-%d')
	nbre_year = 0
	nbre_month = 0
	nbre_day = 0
	while date_debut <= date_fin :
		date_debut = date_debut + relativedelta.relativedelta(years=+1)
		if date_debut > date_fin :
			date_debut = date_debut + relativedelta.relativedelta(years=-1)
			break
		nbre_year +=1
	while date_debut < date_fin:
		date_debut = date_debut + relativedelta.relativedelta(months=+1)
		if date_debut > date_fin :
			break
		nbre_month += 1
	date_debut = date_debut + relativedelta.relativedelta(months=-1)
	nbre_days = (date_fin - date_debut).days
	#print('Années : %s - Mois : %s - JOURS : %s'%(nbre_year, nbre_month,nbre_days))


calcult_date(date_debut="2016-05-28", date_fin="2021-06-14")
