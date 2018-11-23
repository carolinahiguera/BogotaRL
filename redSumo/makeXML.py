import pandas as pd
from pandas import ExcelFile

df = pd.read_excel('turns_aux.xlsx', sheet_name='Sheet3')
namesEdges = df.columns.tolist()
sourceEdge = namesEdges[0]
sinkEdge = namesEdges[1:-1]

num_data = len(df)
xml_turns = open('intervals.xml', 'a')
xml_flows = open('flows.xml', 'a')

xml_turns.write('\t<!-- '+str(namesEdges[-1])+' -->\n')
xml_flows.write('<!-- '+str(namesEdges[-1])+' -->\n')


for i in range(0, num_data-1):
	begin = df[sourceEdge][i]
	end = df[sourceEdge][i+1]
	n = df[namesEdges[-1]][i]
	xml_turns.write('\t<interval begin="'+str(begin)+'" end="'+str(end)+'">\n')
	xml_turns.write('\t\t<fromEdge id="'+str(sourceEdge)+'">\n')
	for j in range(0,len(sinkEdge)):
		p = df[sinkEdge[j]][i]
		xml_turns.write('\t\t <toEdge id="'+str(sinkEdge[j])+'" probability="'+str(p)+'"/>\n')
	xml_turns.write('\t\t</fromEdge>\n')
	xml_turns.write('\t</interval>\n')
	if n != -1:
		xml_flows.write('<flow id="f'+str(i)+'_'+str(sourceEdge)+'" from="'+str(sourceEdge)+'" begin="'+str(begin)+'" end="'+str(end)+'" number="'+str(n)+'"/>\n')
xml_turns.close()
xml_flows.close()

xml_sinks = open('sinks.xml', 'a')
xml_sinks.write('\t<!-- '+str(namesEdges[-1])+' -->\n')
for j in range(0,len(sinkEdge)):
	xml_sinks.write('\t<sink edges="'+str(sinkEdge[j])+'"/>\n')
xml_sinks.close()

	