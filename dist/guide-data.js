// Source-grounded, object-linked beginner journey. These are interpretive views,
// not measured locations or species-level ecological certification.
export const GUIDE_STOPS=[
 {id:'place',short:'一片海',title:'先认识这一小片海',look:'镜头来到礁缘：看近处的珊瑚、中间的砂地和远处逐渐隐入水色的礁面。',text:'这里是浅水斑块礁边缘的示意。真实的佛罗里达群岛里，珊瑚礁、海草床和红树林彼此相连；眼前只做了其中一小块。',note:'海草床与红树林没有在这个场景中建模，也没有复刻某个真实地点。',source:'NOAA · 相连的海洋栖息地',url:'https://floridakeys.noaa.gov/education/habitats.html',position:[1.5,1.6,4.8],target:[-.5,.8,-6],marker:[-.5,.65,-1.5],label:'一块礁缘示意',seconds:24},
 {id:'seabed',short:'看地面',title:'海底也有不同的“地面”',look:'看两个标记：浅色的是砂底，较深、粗糙的是坚硬礁面。',text:'沙地和坚硬礁面不是同一种底质。珊瑚需要固体表面附着；礁体上的凹陷和缝隙，也能为小型动物提供空间。',note:'这里只表现了底质差异；砂粒组成、沉积过程和真实地形并未模拟。',source:'NOAA · 珊瑚礁与附着基底',url:'https://floridakeys.noaa.gov/corals/coralreefs.html',position:[2.4,2.3,7.2],target:[-1.1,.02,2.7],marker:[-1.0108095955155507,-0.1403618167753531,2.8146733771942882],label:'砂底',anchors:[{point:[-1.0108095955155507,-0.1403618167753531,2.8146733771942882],label:'砂底',mesh:'Sand_Rippled_32m'},{point:[-0.3038789189779867,-0.0027501711348518754,3.614089796161855],label:'坚硬礁面',mesh:'Hardbottom_Low_Irregular_Limestone'}],seconds:24},
 {id:'coral',short:'认识珊瑚',title:'像树枝，但珊瑚是动物',look:'靠近这丛细枝，看看它怎样从硬底上向外分叉。',text:'多数珊瑚由许多微小的珊瑚虫组成。硬珊瑚分泌坚硬的碳酸钙骨骼，活组织覆盖在表面。这里参考的是鹿角珊瑚的分枝形态。',note:'模型能展示枝条和群落，不能看清真实珊瑚虫；孔隙纹理也是程序示意。',source:'NOAA · 什么是珊瑚',url:'https://floridakeys.noaa.gov/corals/coralreefs.html',position:[-.6,1.9,5],target:[-2.9,.65,1.7],marker:[-2.9,.65,1.7],label:'分枝硬珊瑚 · 示意',seconds:27},
 {id:'fish',short:'看看鱼',title:'礁上的生物，各有生活方式',look:'镜头跟着一条示意鱼。注意它与枝条的前后位置。',text:'真实珊瑚礁里，有鱼捕食，也有鱼吃藻。礁体的枝条和缝隙提供生活与藏身空间，不能仅凭“都住在海里”就把动物随意放在一起。',note:'这里的鱼未确认到物种，条纹不能用于识别；路线与摆尾是动画，不代表真实觅食或迁徙。',source:'NOAA · 认识礁区生物',url:'https://floridakeys.noaa.gov/education/creature-feature.html',position:[4,3,7],target:[0,1.2,0],marker:[0,1.2,0],label:'通用鱼形 · 非物种鉴定',trackFish:true,seconds:25},
 {id:'light',short:'光与水',title:'为什么光和清澈的水很重要？',look:'再看近处枝条与远处礁面的清晰度，以及照在礁上的光。',text:'多数造礁珊瑚体内住着能光合作用的共生藻。藻利用光制造养分，帮助珊瑚生活，所以透光条件很重要。',note:'这里的蓝绿色、水雾和流动光纹用于帮助观察，不是实测水深、能见度或真实光学计算。',source:'NOAA · 珊瑚生活在怎样的水中',url:'https://oceanservice.noaa.gov/facts/coralwaters.html',position:[5,3.2,9],target:[0,.85,0],marker:[0,.85,0],label:'近处细节 / 远处水雾',seconds:26}
];
export class GuideJourney{
 constructor(stops=GUIDE_STOPS){this.stops=stops;this.index=0;this.active=true;this.playing=false;this.paused=false;this.elapsed=0;this.completed=false;}
 get current(){return this.stops[this.index]}
 go(i){if(!Number.isInteger(i)||i<0||i>=this.stops.length)throw Error('Unknown guide stop');this.index=i;this.active=true;this.paused=false;this.elapsed=0;this.completed=false;return this.current}
 next(){if(this.index===this.stops.length-1){this.completed=true;this.playing=false;return false}this.go(this.index+1);return true}
 previous(){this.go(Math.max(0,this.index-1));return this.current}
 togglePlay(){if(!this.active)this.active=true;this.playing=!this.playing;this.paused=!this.playing;return this.playing}
 pause(){this.playing=false;this.paused=true}
 explore(){this.active=false;this.playing=false;this.paused=true}
 resume(){this.active=true;this.paused=false;this.elapsed=0}
 tick(dt,moving=false){if(!this.active||!this.playing||this.paused||moving)return false;this.elapsed+=Math.max(0,Math.min(dt,.25));if(this.elapsed>=this.current.seconds)return this.next();return false}
}
