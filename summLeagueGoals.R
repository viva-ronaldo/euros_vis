library(dplyr)
library(ggplot2)

holdGoals = data.frame(league=character(),year=character(),goals=numeric(),stringsAsFactors=FALSE)
holdAvGoals = data.frame(league=character(),year=character(),mean=numeric(),stdev=numeric(),stringsAsFactors=FALSE)

.simpleCap <- function(x) {
     s <- strsplit(x, " ")[[1]]
     paste(toupper(substring(s, 1, 1)), substring(s, 2),
           sep = "", collapse = " ")
 }

for (league in c('england/E0','germany/D1','france/F1','italy/I1','spain/SP1')) {
    totGames <- 0
    tot00 <- 0
    totHalves <- c(0,0)
    for (season in c('95-96','99-00','03-04','07-08','11-12')) {
        results <- read.csv(paste0('/home/david/Rpractice/',league,'results',season,'.csv'),
            header=TRUE,sep=",",quote="")    
        cat(league,season,mean(results$FTHG+results$FTAG),sd(results$FTHG+results$FTAG),"\n")

        if (season == '95-96') {
            holdAvGoals <- rbind(holdAvGoals,data.frame(league=.simpleCap(unlist(strsplit(league,'/'))[1]),year=as.character(1900+as.integer(substr(season,4,6))),
                mean=mean(results$FTHG+results$FTAG),stdev=sd(results$FTHG+results$FTAG)))    
            holdGoals <- rbind(holdGoals,data.frame(league=.simpleCap(unlist(strsplit(league,'/'))[1]),year=as.character(1900+as.integer(substr(season,4,6))),
                goals=results$FTHG+results$FTAG))
        } else {
            holdAvGoals <- rbind(holdAvGoals,data.frame(league=.simpleCap(unlist(strsplit(league,'/'))[1]),year=as.character(2000+as.integer(substr(season,4,6))),
                mean=mean(results$FTHG+results$FTAG),stdev=sd(results$FTHG+results$FTAG)))    
            holdGoals <- rbind(holdGoals,data.frame(league=.simpleCap(unlist(strsplit(league,'/'))[1]),year=as.character(2000+as.integer(substr(season,4,6))),
                goals=results$FTHG+results$FTAG))
        }
        tot00 <- tot00 + sum(results$FTHG==0 & results$FTAG==0)
        totGames <- totGames+ nrow(results)
        totHalves <- totHalves + c(sum(results$HTHG+results$HTAG,na.rm=TRUE),
            sum(results$FTHG+results$FTAG-results$HTHG-results$HTAG,na.rm=TRUE))
    }
    cat(sprintf("%.1f%% games 0-0\n",tot00*100/totGames))
    cat(sprintf("%.1f%% goals in first half\n",totHalves[1]*100/(sum(totHalves))))
}

euroGoals <- read.csv('data/euroGoals.csv',header=TRUE,sep=",")
euroGoals <- euroGoals[order(euroGoals$date),]
euroGoals$year <- '1996'
for (year in c(2000,2004,2008,2012)) {
    euroGoals$year[euroGoals$date > year*10000] <- as.character(year)
}
euroGoals$gameNum <- seq(31)
print(euroGoals %>% group_by(stage) %>% summarise(mean(goals)))

holdGoals <- rbind(holdGoals,data.frame(league='euros',year=euroGoals$year,goals=euroGoals$goals))
ggplot(holdGoals) + geom_histogram(aes(x=goals, ..density.., fill=league),position="dodge",binwidth=1)

summEurosKO <- euroGoals %>% filter(stage=='knockout') %>% group_by(year) %>% summarise(mean=mean(goals),stdev=sd(goals))
holdAvGoals <- rbind(holdAvGoals,data.frame(league='Euros knockouts',year=summEurosKO$year,mean=summEurosKO$mean,stdev=summEurosKO$stdev))
summEurosGr <- euroGoals %>% filter(stage=='group') %>% group_by(year) %>% summarise(mean=mean(goals),stdev=sd(goals))
holdAvGoals <- rbind(holdAvGoals,data.frame(league='Euros groups',year=summEurosGr$year,mean=summEurosGr$mean,stdev=summEurosGr$stdev))
ggplot(holdAvGoals) + geom_histogram(aes(x=year,y=mean,fill=league),stat="identity",position="dodge")

write.table(holdAvGoals,file='data/leagueGoals.csv',quote=FALSE,sep=",",row.names=FALSE)

#ggplot(holdGoals,aes(league,goals)) + geom_boxplot()
#ggplot(holdGoals,aes(league,goals)) + geom_violin()
