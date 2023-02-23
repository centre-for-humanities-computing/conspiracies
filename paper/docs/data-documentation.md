# Conspiracies data documentation

*NB: Paths refer to locations on Grundtvig*

## 001_twitter_hope
The folder ``/data/001_twitter_hope/`` on Grundtvig contains nordic tweets continously collected.

| folder | dates | file-type| 
| --- |  --- | --- | 
| ``raw/twitter-da-historic`` | 2020-02-01 - 2020-10-28 | ndjson
| ``raw/nordic-tweets/`` | 2020-04-15 - 2020-05-26 | tsv | 
| ``raw/nordic-tweets-2/`` | 2020-05-27 - 2023-02-19 | tsv | 
| ``preprocessed/da/`` | 2020-02-01 - 2022-08-22 | ndjson | 

**twitter-da-historic**

tweets fetched using twitter premium search api.

stopwords taken from: https://github.com/apache/lucene-solr/blob/master/lucene/analysis/common/src/resources/org/apache/lucene/analysis/snowball/danish_stop.txt

using the following query (twitters requires that you use a search phrase together with lang:da):

```
############## QUERY ######################## 

lang:da (og OR i OR jeg OR det OR at OR en OR den OR til OR er OR som OR på OR de OR med OR han OR af OR for OR ikke OR der OR var OR mig OR sig OR men OR et OR har OR om OR vi OR min OR havde OR ham OR hun OR nu OR over OR da OR fra OR du OR ud OR sin OR dem OR os OR op OR man OR hans OR hvor OR eller OR hvad OR skal OR selv OR her OR alle OR vil OR blev OR kunne OR ind OR når OR være OR dog OR noget OR ville OR jo OR deres OR efter OR ned OR skulle OR denne OR end OR dette OR mit OR også OR under OR have OR dig OR anden OR hende OR mine OR alt OR meget OR sit OR sine OR vor OR mod OR disse OR hvis OR din OR nogle OR hos OR blive OR mange OR ad OR bliver OR hendes OR været OR thi OR jer)

############## QUERY END ####################
```

**nordic-tweets**

Collected with dmi-tcat using the following terms:
aften,aldrig,altid,andet,arbejde,bedste,behøver,blev,blevet,blive,bliver,bruge,burde,død,døde,efter,elsker,endnu,fandt,flere,forstår,fortælle,få,fået,får,før,første,gik,giv,gjorde,gjort,godt,gå,går,gør,gøre,havde,hedder,helt,hende,hendes,hjem,hjælp,hjælpe,hvem,hvis,hvordan,hvorfor,hør,høre,intet,jeres,kender,lidt,længe,meget,må,måde,måske,navn,nogen,noget,nogle,når,nødt,også,på,sagde,sammen,selv,selvfølgelig,sidste,siger,sikker,sikkert,skete,skulle,stadig,sted,står,synes,så,sådan,tager,tid,tilbage,troede,tror,uden,undskyld,venner,vidste,virkelig,væk,vær,være,været,åh,år


**nordic-tweets-2**

Collected with dmi-tcat using the following terms:
aften,aldrig,alltid,altid,andet,arbejde,bedste,behöver,behøver,beklager,berätta,betyr,blev,blevet,blir,blitt,blive,bliver,bruge,burde,bättre,båe,bør,deim,deires,ditt,drar,drepe,dykk,dykkar,där,död,döda,død,døde,efter,elsker,endnu,faen,fandt,feil,fikk,finner,flere,forstår,fortelle,fortfarande,fortsatt,fortælle,från,få,fået,får,fått,förlåt,första,försöker,før,først,første,gick,gikk,gillar,gjennom,gjerne,gjorde,gjort,gjør,gjøre,godt,gå,gång,går,göra,gør,gøre,hadde,hallå,havde,hedder,helt,helvete,hende,hendes,hennes,herregud,hjelp,hjelpe,hjem,hjälp,hjå,hjælp,hjælpe,honom,hossen,hvem,hvis,hvordan,hvorfor,händer,här,håll,håller,hør,høre,hører,igjen,ikkje,ingenting,inkje,inte,intet,jeres,jävla,kanske,kanskje,kender,kjenner,korleis,kvarhelst,kveld,kven,kvifor,känner,ledsen,lenger,lidt,livet,längre,låt,låter,længe,meget,menar,mycket,mykje,må,måde,många,mår,måske,måste,måtte,navn,nogen,noget,nogle,noko,nokon,nokor,nokre,någon,något,några,nån,når,nåt,nødt,också,også,pengar,penger,pratar,prøver,på,redan,rundt,rätt,sagde,saker,samma,sammen,selv,selvfølgelig,sidan,sidste,siger,sikker,sikkert,själv,skete,skjedde,skjer,skulle,sluta,slutt,snakke,snakker,snill,snälla,somt,stadig,stanna,sted,står,synes,säger,sätt,så,sådan,såg,sånn,tager,tiden,tilbage,tilbake,tillbaka,titta,trenger,trodde,troede,tror,två,tycker,tänker,uden,undskyld,unnskyld,ursäkta,uten,varför,varit,varte,veldig,venner,verkligen,vidste,vilken,virkelig,visste,väg,väl,väldigt,vän,vår,våra,våre,væk,vær,være,været,älskar,åh,år,åt,över

**preprocessed/da**

Subset of tweets in the ``raw/`` folder. Contains only tweets with a Danish language flag and the following data for each tweet: 'id', 'created_at', 'text', 'retweet_count', 'favorite_count', 'lang', 'from_user_id'.


## 004_twitter-stopword
The folder ``/data/004_twitter-stopword/`` on Grundtvig contains Danish tweets from 2019-01-01 to 2022-07-31. Every tweets contains the following keys: 'text', 'reply_settings', 'entities', 'conversation_id', 'source', 'created_at', 'lang', 'possibly_sensitive', 'id', 'author_id', 'public_metrics', 'errors', 'includes'.

The tweets were collected with Twitter API V2 (academic track) using the same terms as for *nordic-tweets-2* (See above).