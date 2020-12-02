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
routeAgt{3} = [3,2,1]; %ak13 sentido norte-sur[2,1]
routeAcc{3} = [1,1,1];%[1,1]
routeAgt{4} = [1,4,5,6]; %ak13-cl45 a ak7-cl47
routeAcc{4} = [2,3,1,1];
numRoutes = 4;
nameRoute = {'\textbf{Route 1: Ak7 North-South}','\textbf{Route 2: Ak7 South-North}','\textbf{Route 3: Ak13 North-South}',...
    '\textbf{Route 4: Ak13Cl45 to Ak7Cl47}'};

order = 10;%50

% TF
%path = 'E:\sims_paper\minicityTF';
%addpath(path);

meanSpeed_TF = cell(6,1);
waitTime_TF = cell(6,1);
route_TF = cell(3,1);
for agt=1:6
    for day=1:1
        f1 = ['dfSpeed_testTF_int',num2str(agt-1),'_day',num2str(day-1),'.csv'];
        f2 = ['dfWaiting_testTF_int',num2str(agt-1),'_day',num2str(day-1),'.csv'];
        f3 = ['dfQueue_testTF_int',num2str(agt-1),'_day',num2str(day-1),'.csv'];
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
    %order = 10;
    x = speed./1;
    ma = tsmovavg([x(1:order,:);x],'s',order, 1);
    speed = ma(order+1:end,:);
    meanSpeed_TF{agt} = (speed);
    
    x = time./1;
    ma = tsmovavg([x(1:order,:);x],'s',order, 1);
    time = ma(order+1:end,:);    
    x = queue./1;
    ma = tsmovavg([x(1:order,:);x],'s',order, 1);
    queue = ma(order+1:end,:);
    waitTime_TF{agt} = (time.*60)./queue; %sec
end
for r=1:numRoutes
    aux = zeros(length(waitTime_TF{1}),1);
    for i=1:length(routeAgt{r})
        agt = routeAgt{r}(i);
        acc = routeAcc{r}(i);
        %aux = aux + waitTime_TF{agt}(:,acc) + long{agt}(acc)./meanSpeed_TF{agt}(:,acc);
        aux = aux + waitTime_TF{agt}(:,acc) + long{agt}(acc)/mean(mean(meanSpeed_TF{agt}));
    end
    route_TF{r} = aux./60;
end
%rmpath(path)
%---

% VE
% path = 'E:\sims_paper\Est_VE\marl_ve';
% addpath(path);
% 
% meanSpeed_VE = cell(6,1);
% waitTime_VE = cell(6,1);
% route_VE = cell(3,1);
% for agt=1:6
%     for day=1:5
%         f1 = ['dfSpeed_test_int',num2str(agt-1),'_day',num2str(day-1),'.csv'];
%         f2 = ['dfWaiting_train_int',num2str(agt-1),'_day',num2str(day-1),'.csv'];
%         f3 = ['dfQueue_train_int',num2str(agt-1),'_day',num2str(day-1),'.csv'];
%         if(day==1)
%           speed = csvread(f1,1,2);
%           time = csvread(f2,1,2);
%           queue = csvread(f3,1,2);
%         else
%           speed = speed + csvread(f1,1,2);
%           time = time + csvread(f2,1,2);
%           queue = queue + csvread(f3,1,2);
%         end        
%     end
%     %order = 40;
%     x = speed./5;
%     ma = tsmovavg([x(1:order,:);x],'s',order, 1);
%     speed = ma(order+1:end,:);
%     meanSpeed_VE{agt} = (speed);
%     
%     x = time./5;
%     ma = tsmovavg([x(1:order,:);x],'s',order, 1);
%     time = ma(order+1:end,:);
%     x = queue./5;
%     ma = tsmovavg([x(1:order,:);x],'s',order, 1);
%     queue = ma(order+1:end,:);
%     waitTime_VE{agt} = (time.*60)./queue;
% end
% for r=1:numRoutes
%     aux = zeros(length(waitTime_VE{1}),1);
%     for i=1:length(routeAgt{r})
%         agt = routeAgt{r}(i);
%         acc = routeAcc{r}(i);
%         %aux = aux + waitTime_VE{agt}(:,acc) + long{agt}(acc)./meanSpeed_VE{agt}(:,acc);
%          aux = aux + waitTime_VE{agt}(:,acc) + long{agt}(acc)/mean(mean(meanSpeed_VE{agt}));
%     end
%     route_VE{r} = aux./60;
% end
% rmpath(path)
% %---
% 
% %BR ----------------------
% path = 'E:\sims_paper\br2-14s';
% addpath(path);
% 
% meanSpeed_BR = cell(6,1);
% waitTime_BR = cell(6,1);
% route_BR = cell(3,1);
% for agt=1:6
%     for day=1:5
%         f1 = ['dfMeanSpeed_test_agt',num2str(agt-1),'_day',num2str(day-1),'.csv'];
%         f2 = ['dfWaiting_test_agt',num2str(agt-1),'_day',num2str(day-1),'.csv'];
%         f3 = ['dfQueue_test_agt',num2str(agt-1),'_day',num2str(day-1),'.csv'];
%         if(day==1)
%           speed = csvread(f1,1,2);
%           time = csvread(f2,1,2);
%           queue = csvread(f3,1,2);
%         else
%           speed = speed + csvread(f1,1,2);
%           time = time + csvread(f2,1,2);
%           queue = queue + csvread(f3,1,2);
%         end        
%     end
%     %order = 40;
%     x = speed./5;
%     ma = tsmovavg([x(1:order,:);x],'s',order, 1);
%     speed = ma(order+1:end,:);
%     meanSpeed_BR{agt} = (speed);
%     
%     x = time./5;
%     ma = tsmovavg([x(1:order,:);x],'s',order, 1);
%     time = ma(order+1:end,:);
%     x = queue./5;
%     ma = tsmovavg([x(1:order,:);x],'s',order, 1);
%     queue = ma(order+1:end,:);
%     waitTime_BR{agt} = (time.*60)./queue;
% end
% for r=1:numRoutes
%     aux = zeros(length(waitTime_BR{1}),1);
%     for i=1:length(routeAgt{r})
%         agt = routeAgt{r}(i);
%         acc = routeAcc{r}(i);
%         %aux = aux + waitTime_BR{agt}(:,acc) + long{agt}(acc)./meanSpeed_BR{agt}(:,acc);
%          aux = aux + waitTime_BR{agt}(:,acc) + long{agt}(acc)/mean(mean(meanSpeed_BR{agt}));
%     end
%     route_BR{r} = aux./60;
% end
% rmpath(path)

% IND_Q-LEARNING

%path = 'E:\sims_paper\ind_QLearn';
%addpath(path);

meanSpeed_QL = cell(6,1);
waitTime_QL = cell(6,1);
route_QL = cell(3,1);
for agt=1:6
    for day=1:1
        f1 = ['dfSpeed_test_agt',num2str(agt-1),'_day',num2str(day-1),'.csv'];
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
    x = speed./1;
    ma = tsmovavg([x(1:order,:);x],'s',order, 1);
    speed = ma(order+1:end,:);
    meanSpeed_QL{agt} = (speed);
    
    x = time./1;
    ma = tsmovavg([x(1:order,:);x],'s',order, 1);
    time = ma(order+1:end,:);
    x = queue./1;
    ma = tsmovavg([x(1:order,:);x],'s',order, 1);
    queue = ma(order+1:end,:);
    waitTime_QL{agt} = (time.*60)./queue;
end
for r=1:numRoutes
    aux = zeros(length(waitTime_QL{1}),1);
    for i=1:length(routeAgt{r})
        agt = routeAgt{r}(i);
        acc = routeAcc{r}(i);
        %aux = aux + waitTime_QL{agt}(:,acc) + long{agt}(acc)./meanSpeed_QL{agt}(:,acc);
         aux = aux + waitTime_QL{agt}(:,acc) + long{agt}(acc)/mean(mean(meanSpeed_QL{agt}));
    end
    route_QL{r} = aux./60;
end
%rmpath(path)
%---

% XU METHOD
% path = 'E:\sims_paper\Xu2_br_exp';
% addpath(path);
% 
% meanSpeed_XU = cell(6,1);
% waitTime_XU = cell(6,1);
% route_XU = cell(3,1);
% for agt=1:6
%     for day=1:5
%         f1 = ['dfMeanSpeed_test_agt',num2str(agt-1),'_day',num2str(day-1),'.csv'];
%         f2 = ['dfWaiting_test_agt',num2str(agt-1),'_day',num2str(day-1),'.csv'];
%         f3 = ['dfQueue_test_agt',num2str(agt-1),'_day',num2str(day-1),'.csv'];
%         if(day==1)
%           speed = csvread(f1,1,2);
%           time = csvread(f2,1,2);
%           queue = csvread(f3,1,2);
%         else
%           speed = speed + csvread(f1,1,2);
%           time = time + csvread(f2,1,2);
%           queue = queue + csvread(f3,1,2);
%         end        
%     end
%     %f1 = ['dfMeanSpeed_test_agt',num2str(agt-1),'_day',num2str(0),'.csv'];
%     %speed = csvread(f1,1,2);
%     %order = 40;
%     x = speed./5;
%     ma = tsmovavg([x(1:order,:);x],'s',order, 1);
%     speed = ma(order+1:end,:);
%     meanSpeed_XU{agt} = (speed);
%     
%     x = time./5;
%     ma = tsmovavg([x(1:order,:);x],'s',order, 1);
%     time = ma(order+1:end,:);
%     x = queue./5;
%     ma = tsmovavg([x(1:order,:);x],'s',order, 1);
%     queue = ma(order+1:end,:);
%     waitTime_XU{agt} = (time.*60)./queue;
% end
% for r=1:numRoutes
%     aux = zeros(length(waitTime_XU{1}),1);
%     for i=1:length(routeAgt{r})
%         agt = routeAgt{r}(i);
%         acc = routeAcc{r}(i);
%         %aux = aux + waitTime_XU{agt}(:,acc) + long{agt}(acc)./meanSpeed_XU{agt}(:,acc);
%          aux = aux + waitTime_XU{agt}(:,acc) + long{agt}(acc)/mean(mean(meanSpeed_XU{agt}));
%     end
%     route_XU{r} = aux./60;
% end
% rmpath(path)
%---



meanTravelTime = zeros(numRoutes,5);
stdTravelTime = zeros(numRoutes,5);
clf
figure(1)
for i=1:numRoutes
    subplot(2,2,i)
    t = linspace(0,11,length(route_TF{i}));
    %i6 = find(and(t>6,t<6.1),1);
    %i20 = find(and(t>20,t<20.1),1);
    %plot(t(i6:i20),route_TF{i}(i6:i20),'LineWidth',1.12,'Color','black')
    plot(t,route_TF{i},'LineWidth',1.12,'Color','black')
    hold on
%     t = linspace(0,23,length(route_VE{i}));
%     i6 = find(and(t>6,t<6.1),1);
%     i20 = find(and(t>20,t<20.1),1);
%     plot(t(i6:i20),route_VE{i}(i6:i20),'LineWidth',1.12,'Color','blue')
%     hold on
%     t = linspace(0,23,length(route_BR{i}));
%     i6 = find(and(t>6,t<6.1),1);
%     i20 = find(and(t>20,t<20.1),1);
%     plot(t(i6:i20),route_BR{i}(i6:i20),'LineWidth',1.12,'Color','red')
%     hold on
    t = linspace(0,11,length(route_QL{i}));
    %i6 = find(and(t>6,t<6.1),1);
    %i20 = find(and(t>20,t<20.1),1);
    %plot(t(i6:i20),route_QL{i}(i6:i20),'LineWidth',1.12,'Color',[0,153,0]./255')
    plot(t,route_QL{i},'LineWidth',1.12,'Color',[0,153,0]./255')
    hold on
%     t = linspace(0,23,length(route_XU{i}));
%     i6 = find(and(t>6,t<6.1),1);
%     i20 = find(and(t>20,t<20.1),1);
%     plot(t(i6:i20),route_XU{i}(i6:i20),'LineWidth',1.12,'Color',[237,177,32]./255')
    
    title(nameRoute{i},'Interpreter','latex','fontsize',13);
    xlabel('Hour','Interpreter','latex','fontsize',13)
    ylabel('Waiting time (min)','Interpreter','latex','fontsize',13)
    %xlim([6 21]);
%     tt = cellstr(char(datetime(datevec(t(i6:i20)/24),'Format','HH:mm')));
%     lbl = unique(tt);
%     lbl2 = lbl(1:120:length(lbl));
%     ticks = zeros(1,length(lbl2));
%     tp = t(i6:i20);
%     for jdx=1:length(ticks)
%         ticks(jdx) = tp(find(strcmp(tt, lbl2(jdx)),1));
%     end
%     ax = gca;
%     ax.XTick=ticks;
%     ax.XTickLabel=lbl2;
%     ax.TickLabelInterpreter = 'latex';
%     ax.FontSize = 12;
    
    
    %meanTravelTime(i,:) = [nanmean(route_TF{i}), nanmean(route_VE{i}), nanmean(route_BR{i}), nanmean(route_QL{i}), nanmean(route_XU{i})];
    %stdTravelTime(i,:) = [std(route_TF{i}), std(route_VE{i}), std(route_BR{i}), std(route_QL{i}), std(route_XU{i})];
    %hold on
    %plot(route_BRP{i})
end
disp('done')
% meanTravelTime
% stdTravelTime
%%
% speedTF = mean([mean(meanSpeed_TF{1}),mean(meanSpeed_TF{2}),mean(meanSpeed_TF{3}),...
%     mean(meanSpeed_TF{4}),mean(meanSpeed_TF{5}),mean(meanSpeed_TF{5})])
% speedVE = mean([mean(meanSpeed_VE{1}),mean(meanSpeed_VE{2}),mean(meanSpeed_VE{3}),...
%     mean(meanSpeed_VE{4}),mean(meanSpeed_VE{5}),mean(meanSpeed_VE{5})])
% speedBR = mean([mean(meanSpeed_BR{1}),mean(meanSpeed_BR{2}),mean(meanSpeed_BR{3}),...
%     mean(meanSpeed_BR{4}),mean(meanSpeed_BR{5}),mean(meanSpeed_BR{5})])
% speedQ_ind = mean([mean(meanSpeed_QL{1}),mean(meanSpeed_QL{2}),mean(meanSpeed_QL{3}),...
%     mean(meanSpeed_QL{4}),mean(meanSpeed_QL{5}),mean(meanSpeed_QL{5})])
