clear all; clc; close all;
long = cell(6,1);
long{1} = [94.95, 131.71];
long{2} = [111.88, 79.92];
long{3} = [111.63, 93.98];
long{4} = [129.71, 128.18, 64.77];
long{5} = [116.97, 71.25, 129.71];
long{6} = [114.56, 30.75, 116.97];

routeAgt{1} = [6,5,4]; %ak7 sentido norte-sur
routeAcc{1} = [3,3,2];
routeAgt{2} = [4,5,6]; %ak7 sentido sur-norte
routeAcc{2} = [1,1,1];
routeAgt{3} = [3,2,1]; %ak13 sentido norte-sur
routeAcc{3} = [1,1,1];
routeAgt{4} = [1,4,5,6]; %ak13-cl45 a ak7-cl47
routeAcc{4} = [2,3,1,1];
numRoutes = 4;
nameRoute = {'\textbf{Ak7 sentido N-S}','\textbf{Ak7 sentido S-N}','\textbf{Ak13 sentido N-S}',...
    '\textbf{Ak13Cl45 a Ak7Cl47}'};

order = 40;

%BR
path = 'E:\sims_paper\ind_QLearn';
addpath(path);

meanSpeed_BR = cell(6,1);
waitTime_BR = cell(6,1);
queue_BR = cell(6,1);
route_BR = cell(3,1);
for agt=1:6
    for day=1:5
        f1 = ['dfMeanSpeed_test_agt',num2str(agt-1),'_day',num2str(day-1),'.csv'];
        f2 = ['dfWaiting_test_agt',num2str(agt-1),'_day',num2str(day-1),'.csv'];
        f3 = ['dfQueue_test_agt',num2str(agt-1),'_day',num2str(day-1),'.csv'];
        if(day==1)
          speed = csvread(f1,1,2);
          time = csvread(f2,1,2);
          queue = csvread(f3,1,2);
        else
          speed = speed + csvread(f1,1,2);
          time = time + csvread(f2,1,2);
          queue = queue + csvread(f3,1,2);
        end        
    end
    %f1 = ['dfMeanSpeed_test_agt',num2str(agt-1),'_day',num2str(0),'.csv'];
    %speed = csvread(f1,1,2);
    %order = 40;
    x = speed./5;
    ma = tsmovavg([x(1:order,:);x],'s',order, 1);
    speed = ma(order+1:end,:);
    meanSpeed_BR{agt} = (speed);
    
    x = time./5;
    ma = tsmovavg([x(1:order,:);x],'s',order, 1);
    time = ma(order+1:end,:);
    x = queue./5;
    ma = tsmovavg([x(1:order,:);x],'s',order, 1);
    queue = ma(order+1:end,:);
    waitTime_BR{agt} = (time./queue).*60;
    queue_BR{agt} = (queue);
end

%read actions
dayTest = 4;
file = ['dfActions_test_day',num2str(dayTest),'.csv'];
actions = csvread(file,1,1);
inGreen = 14;
%% tiempo entre intersecciones
timeTray = cell(numRoutes,1);
for r=1:numRoutes
    timeTray{r}=zeros(1,length(routeAgt{r}));
    for i=1:length(routeAgt{r})
        agt = routeAgt{r}(i);
        acc = routeAcc{r}(i);
        timeTray{r}(i) = long{agt}(acc)./meanSpeed_BR{agt}(acc) +4 ;
    end
end

%% graficar diagrama
h_in = 17; %17.92
h_fi = 20; %18.09
interval = 10;
route = 1;
agtPlot = routeAgt{route};
lblY = cell(1,length(agtPlot));
for i=1:length(agtPlot)
    lblY{i} = ['agent ',num2str(agtPlot(i))];
end

for xx=1:60%h_in:interval/60:h_fi
h_ini = (h_in*3600 + interval*60*(xx-1))/3600;
h_fin = (h_in*3600 + interval*60*(xx))/3600;

i = find(actions(:,1)>=h_ini, 1);
j = find(actions(:,1)>=h_fin, 1);

act = cell(6,1);
queues =  cell(6,1);
figure(1)
clf
phases = cell(6,1);
for idx=1:length(agtPlot)
    agt = agtPlot(idx);
    act{agt}=actions(i:j, agt+1);
    queues{agt} = queue_BR{agt}(i:j, routeAcc{route}(idx));
    t = linspace(h_ini*3600, h_ini*3600 + interval*60, length(act{agt}))./3600;
    phases{agt}=[t',act{agt}];
    tt = cellstr(char(datetime(datevec(t/24),'Format','HH:mm')));
    lbl = unique(tt);
    lbl2 = lbl(1:2:length(lbl));
    %subplot(length(agtPlot),1,idx)
    %subplot(length(agtPlot),2,1:2:(2*length(agtPlot)))
    stairs2(1:length(t),act{agt},idx,0)
    %ylabel(['agente ',num2str(agt)])
    ticks = zeros(1,length(lbl2));
    for jdx=1:length(ticks)
        ticks(jdx) = find(strcmp(tt, lbl2(jdx)),1);
    end
    ax = gca;
    ax.XTick=ticks;
    ax.XTickLabel=lbl;
    ax.YTick=1:length(agtPlot);
    ax.YTickLabel=lblY;
    ax.TickLabelInterpreter = 'latex';
    ax.FontSize = 11;
    xlabel('Hour','Interpreter','latex','fontsize',11)
      
end
grid on  
legend({'phase 0','phase 2'},'Location','northoutside','Orientation','horizontal','Interpreter','latex','FontSize',10)

%Check when is ph0
phase = 0;
posPH = cell(6,1);
for i=1:length(agtPlot)
    agt = agtPlot(i);
    posPH{agt} = countPh(phases{agt}(:,2),phase);
end

lines = {};

for i=1:length(posPH{agtPlot(1)})
    if(i==11)
        i;
    end
    times=[]; times2=[];lvl=[];
    v = 1:length(phases{agtPlot(1)}(:,1));
    times(1)=phases{agtPlot(1)}(posPH{agtPlot(1)}(i),1);
    times2(1)=interp1(phases{agtPlot(1)}(:,1),v,times(1));
    lvl(1)=1;
    for j=2:length(agtPlot)
        a = find(agtPlot==agtPlot(j));
        times(j)=((times(j-1)*3600)+timeTray{route}(a))/3600;
        idx = find(phases{agtPlot(j)}(:,1)<times(j),1,'last');
        if(phases{agtPlot(j)}(idx,2)==phase)
            v = 1:length(phases{agtPlot(j)}(:,1));
            times2(j)=interp1(phases{agtPlot(j)}(:,1),v,times(j));
            lvl(j) = j;
        else
            j = -1;
            break
        end
    end
    if(j~=-1)
        for k=1:length(times2)-1
            lines{end+1}=[times2(k),lvl(k);times2(k+1),lvl(k+1)];
        end
    end
    
    
end

% for i=1:length(agtPlot)-1
%     to = agtPlot(i+1);
%     from = agtPlot(i);   
%     for j=1:length(posPH{from})
%         cTime = phases{from}(posPH{from}(j),1);
%         nTime = ((cTime*3600)+timeTray{route}(i))/3600;
%         idx = find(phases{to}(:,1)<nTime,1,'last');
%         if(phases{to}(idx,2)==phase)
%             v = 1:length(phases{from}(:,1));
%             a = interp1(phases{from}(:,1),v,cTime);
%             b = interp1(phases{to}(:,1),v,nTime);
%             lines{end+1}=[a,i; b,i+1];
%         end
%     end
% end
%subplot(length(agtPlot),2,1:2:(2*length(agtPlot)))
for i=1:length(lines)
    hold on
    plot(lines{i}(:,1),lines{i}(:,2),'--k')
end



pause()
end


