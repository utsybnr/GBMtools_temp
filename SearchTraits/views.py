from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Sum, Avg, StdDev, F, Q
from django.db import connection
import numpy as np
import time

from .forms import SearchForm, SearchForm_2021Ver, baseForm, ChartForm
from .models import WordTag

from Chartview.models import Status, Unit


# Create your views here.

MELEE_WEAPON =[
    "サーベル",
    "ダブルサーベル",
    "アックス",
    "大剣",
    "ランス",
    "モジュール",
    "ムチ",
    "ツインブレード"
]
SHOT_WEAPON = [
    "ライフル",
    "ロングライフル",
    "ダブルライフル",
    "マシンガン",
    "バズーカ",
    "ガトリングガン"
]

base = baseForm()

class SearchTraitsClass(TemplateView):
    template_name = 'search.html'

def SearchTraitsForm(request):
    form = SearchForm()
    return render(request, "search.html", {"base": base, "form": form})

def SearchTraitsForm_2021Ver(request):
    form = SearchForm_2021Ver()
    return render(request, "search.html", {"base": base, "form": form})

def index(request, exception):
    return render(request, "index.html", {"base": base})

def BadgeForm(request):
    return render(request, "badge.html", {"base": base})

def ListView(request):
    form = SearchForm()
    
    #部位
    if request.GET.get('SelectCategory')=='MeleeWeapon':
        if request.GET.get('MeleeWeapon'):
            SelectedCategoryList = []
            SelectedCategoryList.append(request.GET.get('MeleeWeapon'))
            form.fields['MeleeWeapon'].initial = request.GET.get('MeleeWeapon')       
        else:
            SelectedCategoryList = MELEE_WEAPON

    elif request.GET.get('SelectCategory')=='ShotWeapon':
        if request.GET.get('ShotWeapon'):
            SelectedCategoryList = []
            SelectedCategoryList.append(request.GET.get('ShotWeapon'))           
            form.fields['ShotWeapon'].initial = request.GET.get('ShotWeapon')
        else:
            SelectedCategoryList = SHOT_WEAPON

    elif  'SelectCategory' in request.GET:
        SelectedCategoryList = []
        SelectedCategoryList.append(request.GET.get('SelectCategory'))
    else:
        SelectedCategoryList = []
        SelectedCategoryList.append('Head')

    form.fields['SelectCategory'].initial = request.GET.get('SelectCategory') if 'SelectCategory' in request.GET else 'Head'

    StatusList = Status.objects.filter(Category__in=SelectedCategoryList)

    #一体型パーツ
    if not request.GET.get('withCombinedParts'):
        StatusList = StatusList.filter(Q(CombinedCategory="")|Q(CombinedCategory__isnull=True))
    else:
        form.fields['withCombinedParts'].initial = request.GET.get('withCombinedParts')

    #特性
    SearchEffect1 = request.GET.get('Effect1')
    SearchEffect2 = request.GET.get('Effect2')
    DictTraitOption = {
        'TraitAttribute': request.GET.get('TraitAttribute'),
        'TraitWordtag': [request.GET.get('TraitWordtag1'),request.GET.get('TraitWordtag2'),request.GET.get('TraitWordtag3')],
        'isArenaTraits': request.GET.get('isArenaTraits'),
        'isSoloTraits': request.GET.get('isSoloTraits'),
    }

    form.fields['TraitAttribute'].initial = request.GET.get('TraitAttribute')
    form.fields['TraitWordtag1'].initial = request.GET.get('TraitWordtag1')
    form.fields['TraitWordtag2'].initial = request.GET.get('TraitWordtag2')
    form.fields['TraitWordtag3'].initial = request.GET.get('TraitWordtag3')
    form.fields['isArenaTraits'].initial = request.GET.get('isArenaTraits')
    form.fields['isSoloTraits'].initial = request.GET.get('isSoloTraits')

    if SearchEffect1 or SearchEffect2:
        #records = (query1 | query2).distinct()
        #別オブジェクトでスキルのIDを取得→id=でフィルタ
        #https://qiita.com/virtual_techX/items/fc31445d6836c983affc
        SearchTraitObject = Traits1Filter(Status.objects.all(), SearchEffect1, DictTraitOption) if SearchEffect1 else Status.objects.all()
        SearchTraitObject = Traits2Filter(SearchTraitObject, SearchEffect2, DictTraitOption) if SearchEffect2 else SearchTraitObject

        SearchTraitReverseObject = Traits1Filter(Status.objects.all(), SearchEffect2, DictTraitOption) if SearchEffect2 else Status.objects.all()
        SearchTraitReverseObject = Traits2Filter(SearchTraitReverseObject, SearchEffect1, DictTraitOption) if SearchEffect1 else SearchTraitReverseObject

        SearchTraitObjectAll = SearchTraitReverseObject | SearchTraitObject 

        TraitidList = list(SearchTraitObjectAll.distinct().values_list("id", flat=True))
        StatusList = StatusList.filter(id__in=TraitidList)

    form.fields['Effect1'].initial = request.GET.get('Effect1')
    form.fields['Effect2'].initial = request.GET.get('Effect2')

    #ジョブライセンス
    if request.GET.get('Joblisence'):
        StatusList = StatusList.filter(Joblisence__icontains=request.GET.get('Joblisence'))
        form.fields['Joblisence'].initial = request.GET.get('Joblisence')

    #属性
    if request.GET.get('Attribute'):
        StatusList = StatusList.filter(Attribute=request.GET.get('Attribute'))
        form.fields['Attribute'].initial = request.GET.get('Attribute')

    #タグ1
    if request.GET.get('Wordtag1'):
        StatusList = WordtagFilter(StatusList, request.GET.get('Wordtag1'), request.GET.get('includeSubWordtag'))
        form.fields['includeSubWordtag'].initial = request.GET.get('includeSubWordtag')
        form.fields['Wordtag1'].initial = request.GET.get('Wordtag1')

    #タグ2
    if request.GET.get('Wordtag2'):
        StatusList = WordtagFilter(StatusList, request.GET.get('Wordtag2'), request.GET.get('includeSubWordtag'))
        form.fields['includeSubWordtag'].initial = request.GET.get('includeSubWordtag')
        form.fields['Wordtag2'].initial = request.GET.get('Wordtag2')

    #AIタイプ(距離)
    if request.GET.get('AIDistance'):
        StatusList = StatusList.filter(AItype__icontains=request.GET.get('AIDistance'))
        form.fields['AIDistance'].initial = request.GET.get('AIDistance')

    #AIタイプ(型)
    if request.GET.get('AIType'):
        StatusList = StatusList.filter(AItype__icontains=request.GET.get('AIType'))
        form.fields['AIType'].initial = request.GET.get('AIType')

    #改造
    if request.GET.get('isAlter'):
        StatusList = StatusList.filter(PartsName__icontains='【改造')
        form.fields['isAlter'].initial = request.GET.get('isAlter')

    #ギア有無、表示ステータス
    IswithGear = True if request.GET.get('withGear')=='on' and request.GET.get('SelectStatusType') in ['MeleeATK','ShotATK'] else False
    if IswithGear :
        form.fields['withGear'].initial = request.GET.get('withGear')

    SelectedStatus = request.GET.get('SelectStatusType') if 'SelectStatusType' in request.GET else 'Armor'
    form.fields['SelectStatusType'].initial = SelectedStatus

    #選択値をSelectedStatusに名前変更した上でソート。
    #https://opendata-web.site/blog/entry/23/
    StatusList = StatusList \
    .annotate(Lv99MeleeATKwithGear=F('Lv99MeleeATK')+0.4*F('Lv99MeleeDEF')) \
    .annotate(Lv99ShotATKwithGear=F('Lv99ShotATK')+0.4*F('Lv99ShotDEF')) \
    .annotate(SelectedStatus=F('Lv99'+SelectedStatus+'withGear' if IswithGear else 'Lv99'+SelectedStatus)).order_by('SelectedStatus').reverse()[:50]

    Isinitial = True if not request.GET else False

    return render(request, "ChartView/list.html", \
        {"base": base, "form": form, "StatusList":StatusList, "SelectedStatus":SelectedStatus, "Isinitial":Isinitial})


def CombinationListView(request):
    #変換ギアが非活性のまま
    #検索自体が重いので軽量化→statusにインデックス？
    form = SearchForm()
   
    #部位
    if request.GET.get('SelectCategory')=='MeleeWeapon':
        if request.GET.get('MeleeWeapon'):
            SelectedCategoryList = []
            SelectedCategoryList.append(request.GET.get('MeleeWeapon'))
            form.fields['MeleeWeapon'].initial = request.GET.get('MeleeWeapon')       
        else:
            SelectedCategoryList = MELEE_WEAPON

    elif request.GET.get('SelectCategory')=='ShotWeapon':
        if request.GET.get('ShotWeapon'):
            SelectedCategoryList = []
            SelectedCategoryList.append(request.GET.get('ShotWeapon'))           
            form.fields['ShotWeapon'].initial = request.GET.get('ShotWeapon')
        else:
            SelectedCategoryList = SHOT_WEAPON

    elif  'SelectCategory' in request.GET:
        SelectedCategoryList = []
        SelectedCategoryList.append(request.GET.get('SelectCategory'))
    else:
        SelectedCategoryList = []
        SelectedCategoryList.append('Head')

    SelectedCategoryQuery = "('dummy'"
    for SelectedCategory in SelectedCategoryList:
        SelectedCategoryQuery += ", '"+ SelectedCategory +"'"
    SelectedCategoryQuery += ")"
 
    form.fields['SelectCategory'].initial = request.GET.get('SelectCategory') if 'SelectCategory' in request.GET else 'Head'

    #属性
    if request.GET.get('Attribute'):
        AttributeQuery = " AND MainAttribute = '" + request.GET.get('Attribute') +"'"
        form.fields['Attribute'].initial = request.GET.get('Attribute')
    else:
        AttributeQuery = ""

    #タグ1
    if request.GET.get('Wordtag1'):
        if request.GET.get('includeSubWordtag'):
            Wordtag1Query = " AND ("\
                + "MainSpeedWordtag1 = '" + request.GET.get('Wordtag1') +"'"\
                + "OR MainSpeedWordtag2 = '" + request.GET.get('Wordtag1') +"'"\
                + "OR MainTechniqueWordtag1 = '" + request.GET.get('Wordtag1') +"'"\
                + "OR MainTechniqueWordtag2 = '" + request.GET.get('Wordtag1') +"'"\
                + "OR MainPowerWordtag1 = '" + request.GET.get('Wordtag1') +"'"\
                + "OR MainPowerWordtag2 = '" + request.GET.get('Wordtag1') +"'"\
                + "OR SubSpeedWordtag1 = '" + request.GET.get('Wordtag1') +"'"\
                + "OR SubSpeedWordtag2 = '" + request.GET.get('Wordtag1') +"'"\
                + "OR SubTechniqueWordtag1 = '" + request.GET.get('Wordtag1') +"'"\
                + "OR SubTechniqueWordtag2 = '" + request.GET.get('Wordtag1') +"'"\
                + "OR SubPowerWordtag1 = '" + request.GET.get('Wordtag1') +"'"\
                + "OR SubPowerWordtag2 = '" + request.GET.get('Wordtag1') +"'"\
                + ")"
        else:
            Wordtag1Query = " AND ("\
                + "Main.Wordtag1 = '" + request.GET.get('Wordtag1') +"'"\
                + "OR Main.Wordtag2 = '" + request.GET.get('Wordtag1') +"'"\
                + "OR SubCalc.Wordtag1 = '" + request.GET.get('Wordtag1') +"'"\
                + "OR SubCalc.Wordtag2 = '" + request.GET.get('Wordtag1') +"'"\
                + ")"        
        form.fields['includeSubWordtag'].initial = request.GET.get('includeSubWordtag')
        form.fields['Wordtag1'].initial = request.GET.get('Wordtag1')
    else:
        Wordtag1Query = ""

    #タグ2
    if request.GET.get('Wordtag2'):
        if request.GET.get('includeSubWordtag'):
            Wordtag2Query = " AND ("\
                + "MainSpeedWordtag1 = '" + request.GET.get('Wordtag2') +"'"\
                + "OR MainSpeedWordtag2 = '" + request.GET.get('Wordtag2') +"'"\
                + "OR MainTechniqueWordtag1 = '" + request.GET.get('Wordtag2') +"'"\
                + "OR MainTechniqueWordtag2 = '" + request.GET.get('Wordtag2') +"'"\
                + "OR MainPowerWordtag1 = '" + request.GET.get('Wordtag2') +"'"\
                + "OR MainPowerWordtag2 = '" + request.GET.get('Wordtag2') +"'"\
                + "OR SubSpeedWordtag1 = '" + request.GET.get('Wordtag2') +"'"\
                + "OR SubSpeedWordtag2 = '" + request.GET.get('Wordtag2') +"'"\
                + "OR SubTechniqueWordtag1 = '" + request.GET.get('Wordtag2') +"'"\
                + "OR SubTechniqueWordtag2 = '" + request.GET.get('Wordtag2') +"'"\
                + "OR SubPowerWordtag1 = '" + request.GET.get('Wordtag2') +"'"\
                + "OR SubPowerWordtag2 = '" + request.GET.get('Wordtag2') +"'"\
                + ")"
        else:
            Wordtag2Query = " AND ("\
                + "Main.Wordtag1 = '" + request.GET.get('Wordtag2') +"'"\
                + "OR Main.Wordtag2 = '" + request.GET.get('Wordtag2') +"'"\
                + "OR SubCalc.Wordtag1 = '" + request.GET.get('Wordtag2') +"'"\
                + "OR SubCalc.Wordtag2 = '" + request.GET.get('Wordtag2') +"'"\
                + ")"        
        form.fields['includeSubWordtag'].initial = request.GET.get('includeSubWordtag')
        form.fields['Wordtag2'].initial = request.GET.get('Wordtag2')
    else:
        Wordtag2Query = ""

    #一体型パーツ
    if not request.GET.get('withCombinedParts'):
        withCombinedPartsQuery = " AND (Main.CombinedCategory IS NULL OR Main.CombinedCategory ='') "
    else:
        withCombinedPartsQuery = ''
        form.fields['withCombinedParts'].initial = request.GET.get('withCombinedParts')

    SelectedStatus = request.GET.get('SelectStatusType') if 'SelectStatusType' in request.GET else 'Armor'
    form.fields['SelectStatusType'].initial = SelectedStatus

    t3 = time.time()
    cursor = connection.cursor()

    inputQueryBase = """
        SELECT 
            Main.Id AS MainId,
            Main.PartsName AS MainPartsName,
            Main.Attribute AS MainAttribute,
            Main.CombinedCategory AS MainCombinedCategory,
            SubCalc.Id AS SubId,
            SubCalc.PartsName AS SubPartsName,
            SubCalc.Attribute AS SubAttribute,
            CASE
                WHEN (Main.CombinedCategory IS NULL OR Main.CombinedCategory = '') 
                AND NOT(SubCalc.CombinedCategory IS NULL OR SubCalc.CombinedCategory = '')
                    THEN Main.@SelectedStatus @addMainGearQuery + 0.5*(SubCalc.TagCalcStatus + SubCalc.BigCalcStatus @addSubGearQuery) 
                when NOT(Main.CombinedCategory IS NULL OR Main.CombinedCategory = '') 
                AND (SubCalc.CombinedCategory IS NULL OR SubCalc.CombinedCategory = '')
                    THEN Main.@SelectedStatus @addMainGearQuery + 2*(SubCalc.TagCalcStatus + SubCalc.BigCalcStatus @addSubGearQuery)
                ELSE
                    Main.@SelectedStatus @addMainGearQuery + SubCalc.TagCalcStatus + SubCalc.BigCalcStatus @addSubGearQuery
            END AS SelectedStatus
            @WordtagQuery
        FROM
            Chartview_Status AS Main
        INNER JOIN
            (
                SELECT
                    Sub.id AS Id,
                    Sub.CombinedCategory AS CombinedCategory,
                    Sub.PartsName AS PartsName,
                    Sub.Category AS Category,                        
                    Sub.Attribute AS Attribute,                        
                    Sub.MaxRarity AS MaxRarity,                        
                    Sub.Wordtag1 AS Wordtag1,                        
                    Sub.Wordtag2 AS Wordtag2,                        
                    Main.id AS MainId,
                    CASE
                        WHEN REPLACE(REPLACE(Main.PartsName,'【改造】',''),'【改造BIG】','')=REPLACE(REPLACE(Sub.PartsName,'【改造】',''),'【改造BIG】','')
                            THEN 0.35*Sub.@SelectedStatus
                        WHEN (Main.Wordtag1=Sub.Wordtag1 AND Main.Wordtag2=Sub.Wordtag2)
                        OR(Main.Wordtag1=Sub.Wordtag2 AND Main.Wordtag2=Sub.Wordtag1)
                            THEN 0.25*Sub.@SelectedStatus
                        WHEN Main.Wordtag1=Sub.Wordtag1 OR Main.Wordtag2=Sub.Wordtag2
                            THEN 0.15*Sub.@SelectedStatus
                        ELSE 
                            0.05*Sub.@SelectedStatus
                    END AS TagCalcStatus,
                    CASE
                        WHEN (Main.PartsName LIKE '【改造BIG】%' AND Sub.PartsName NOT LIKE '【改造BIG】%')
                        OR(Main.PartsName NOT LIKE '【改造BIG】%' AND Sub.PartsName LIKE '【改造BIG】%')
                            THEN 0.2*Sub.@SelectedStatus
                        ELSE 
                            0
                    END AS BigCalcStatus
                    @getDEFQuery
                FROM 
                    Chartview_Status AS Main
                INNER JOIN 
                    Chartview_Status AS Sub
                    ON Main.Category = Sub.Category
                WHERE 
                    Main.Category IN @CategoryList
            ) AS SubCalc
        ON SubCalc.MainId = Main.id
    """
    WordtagQuerySELECTMainRarity6 = """,
            NULL AS MainSpeedWordtag1, 
            NULL AS MainSpeedWordtag2, 
            NULL AS MainTechniqueWordtag1, 
            NULL AS MainTechniqueWordtag2, 
            NULL AS MainPowerWordtag1, 
            NULL AS MainPowerWordtag2,
            NULL AS MainSpeedAttribute, 
            NULL AS MainTechniqueAttribute, 
            NULL AS MainPowerAttribute
    """
    WordtagQuerySELECTSubRarity6 = """, 
            NULL AS SubSpeedWordtag1, 
            NULL AS SubSpeedWordtag2, 
            NULL AS SubTechniqueWordtag1, 
            NULL AS SubTechniqueWordtag2, 
            NULL AS SubPowerWordtag1, 
            NULL AS SubPowerWordtag2,
            NULL AS SubSpeedAttribute, 
            NULL AS SubTechniqueAttribute, 
            NULL AS SubPowerAttribute
    """
    WordtagQuerySELECTMainRarity7 = """,
            Main_Speed.Wordtag1 AS MainSpeedWordtag1, 
            Main_Speed.Wordtag2 AS MainSpeedWordtag2, 
            Main_Technique.Wordtag1 AS MainTechniqueWordtag1, 
            Main_Technique.Wordtag2 AS MainTechniqueWordtag2, 
            Main_Power.Wordtag1 AS MainPowerWordtag1, 
            Main_Power.Wordtag2 AS MainPowerWordtag2,
            Main_Speed.Attribute AS MainSpeedAttribute, 
            Main_Technique.Attribute AS MainTechniqueAttribute, 
            Main_Power.Attribute AS MainPowerAttribute
    """
    WordtagQuerySELECTSubRarity7 = """, 
            Sub_Speed.Wordtag1 AS SubSpeedWordtag1, 
            Sub_Speed.Wordtag2 AS SubSpeedWordtag2, 
            Sub_Technique.Wordtag1 AS SubTechniqueWordtag1, 
            Sub_Technique.Wordtag2 AS SubTechniqueWordtag2, 
            Sub_Power.Wordtag1 AS SubPowerWordtag1, 
            Sub_Power.Wordtag2 AS SubPowerWordtag2,
            Sub_Speed.Attribute AS SubSpeedAttribute, 
            Sub_Technique.Attribute AS SubTechniqueAttribute, 
            Sub_Power.Attribute AS SubPowerAttribute
    """
    WordtagQueryWHEREMainRarity7= \
    """
        LEFT JOIN
            Chartview_Status AS Main_Speed
        ON
            Main_Speed.PartsName = REPLACE(REPLACE(Main.PartsName,'【改造】',''),'【改造BIG】','')
            AND Main_Speed.Category = Main.Category        
            AND Main_Speed.Attribute = 'Speed' 
        LEFT JOIN
            Chartview_Status AS Main_Technique
        ON
            Main_Technique.PartsName = REPLACE(REPLACE(Main.PartsName,'【改造】',''),'【改造BIG】','')
            AND Main_Technique.Category = Main.Category
            AND Main_Technique.Attribute = 'Technique'
        LEFT JOIN
            Chartview_Status AS Main_Power
        ON
            Main_Power.PartsName = REPLACE(REPLACE(Main.PartsName,'【改造】',''),'【改造BIG】','')
            AND Main_Power.Category = Main.Category
            AND Main_Power.Attribute = 'Power'
    """

    WordtagQueryWHERESubRarity7= \
    """
        LEFT JOIN
            Chartview_Status AS Sub_Speed
        ON
            Sub_Speed.PartsName = REPLACE(REPLACE(SubCalc.PartsName,'【改造】',''),'【改造BIG】','')
            AND Sub_Speed.Category = SubCalc.Category
            AND Sub_Speed.Attribute = 'Speed'
        LEFT JOIN
            Chartview_Status AS Sub_Technique
        ON
            Sub_Technique.PartsName = REPLACE(REPLACE(SubCalc.PartsName,'【改造】',''),'【改造BIG】','')
            AND Sub_Technique.Category = SubCalc.Category
            AND Sub_Technique.Attribute = 'Technique'
        LEFT JOIN
            Chartview_Status AS Sub_Power
        ON
            Sub_Power.PartsName = REPLACE(REPLACE(SubCalc.PartsName,'【改造】',''),'【改造BIG】','')
            AND Sub_Power.Category = SubCalc.Category
            AND Sub_Power.Attribute = 'Power'
    """

    inputQuerywhere = """
        WHERE 1=1
        @Combined
        @Attribute
        @Wordtag1
        @Wordtag2
    """

    inputQueryMainRarity6SubRarity6 = inputQueryBase.replace('@WordtagQuery', WordtagQuerySELECTMainRarity6+WordtagQuerySELECTSubRarity6)
    inputQueryMainRarity7SubRarity6 = inputQueryBase.replace('@WordtagQuery', WordtagQuerySELECTMainRarity7+WordtagQuerySELECTSubRarity6) 
    inputQueryMainRarity6SubRarity7 = inputQueryBase.replace('@WordtagQuery', WordtagQuerySELECTMainRarity6+WordtagQuerySELECTSubRarity7)
    inputQueryMainRarity7SubRarity7 = inputQueryBase.replace('@WordtagQuery', WordtagQuerySELECTMainRarity7+WordtagQuerySELECTSubRarity7)

    if request.GET.get('withGear')=='on' and (SelectedStatus =='MeleeATK' or SelectedStatus =='ShotATK'):
        #ギア込み
        print(form.fields['withGear'].initial)
        form.fields['withGear'].initial = request.GET.get('withGear')
        SelectedDEF = SelectedStatus.replace("ATK","DEF")
        addMainGearQuery = " +0.4*Main.@SelectedDEF"
        addSubGearQuery = " +0.4*(SubCalc.TagCalcDEF + SubCalc.BigCalcDEF)"
        getDEFQuery  = """
        ,
                    CASE
                        WHEN REPLACE(REPLACE(Main.PartsName,'【改造】',''),'【改造BIG】','')=REPLACE(REPLACE(Sub.PartsName,'【改造】',''),'【改造BIG】','')
                            THEN 0.35*Sub.@SelectedDEF
                        WHEN (Main.Wordtag1=Sub.Wordtag1 AND Main.Wordtag2=Sub.Wordtag2)
                        OR(Main.Wordtag1=Sub.Wordtag2 AND Main.Wordtag2=Sub.Wordtag1)
                            THEN 0.25*Sub.@SelectedDEF
                        WHEN Main.Wordtag1=Sub.Wordtag1 OR Main.Wordtag2=Sub.Wordtag2
                            THEN 0.15*Sub.@SelectedDEF
                        ELSE 
                            0.05*Sub.@SelectedDEF
                    END AS TagCalcDEF,
                    CASE
                        WHEN (Main.PartsName LIKE '【改造BIG】%' AND Sub.PartsName NOT LIKE '【改造BIG】%')
                        OR(Main.PartsName NOT LIKE '【改造BIG】%' AND Sub.PartsName LIKE '【改造BIG】%')
                            THEN 0.2*Sub.@SelectedDEF
                        ELSE 
                            0
                    END AS BigCalcDEF
        """
    else:
        SelectedDEF = ""
        addMainGearQuery = ""
        addSubGearQuery = ""
        getDEFQuery = ""


    inputQuery \
    = inputQueryMainRarity6SubRarity6\
    + inputQuerywhere

    if request.GET.get('includeSubWordtag'):
        inputQuery += \
            """ 
                AND (Main.MaxRarity = 6 AND SubCalc.MaxRarity = 6)
            UNION ALL
            """\
            + inputQueryMainRarity7SubRarity6\
            + WordtagQueryWHEREMainRarity7\
            + inputQuerywhere\
            + """ 
                AND (Main.MaxRarity = 7 AND SubCalc.MaxRarity = 6)
            UNION ALL
            """\
            + inputQueryMainRarity6SubRarity7\
            + WordtagQueryWHERESubRarity7\
            + inputQuerywhere\
            + """ 
                AND (Main.MaxRarity = 6 AND SubCalc.MaxRarity = 7)
            UNION ALL
            """\
            + inputQueryMainRarity7SubRarity7\
            + WordtagQueryWHEREMainRarity7 + WordtagQueryWHERESubRarity7\
            + inputQuerywhere\
            +   """
                AND (Main.MaxRarity = 7 AND SubCalc.MaxRarity = 7) 
            """

    inputQuery += """
            ORDER BY SelectedStatus DESC
            LIMIT 50
    """
            
    inputQuery = inputQuery.replace('@getDEFQuery', getDEFQuery)
    inputQuery = inputQuery.replace('@addMainGearQuery', addMainGearQuery)
    inputQuery = inputQuery.replace('@addSubGearQuery', addSubGearQuery)
    inputQuery = inputQuery.replace('@SelectedStatus', 'Lv99'+SelectedStatus)
    inputQuery = inputQuery.replace('@SelectedDEF', 'Lv99'+SelectedDEF)
    inputQuery = inputQuery.replace('@CategoryList', SelectedCategoryQuery)
    inputQuery = inputQuery.replace('@Combined', withCombinedPartsQuery)
    inputQuery = inputQuery.replace('@Attribute', AttributeQuery)
    inputQuery = inputQuery.replace('@Wordtag1', Wordtag1Query)
    inputQuery = inputQuery.replace('@Wordtag2', Wordtag2Query)


    cursor.execute(inputQuery)

    CombinationList = cursor.fetchall()
    t4 = time.time()
    print("rawsql:"+str(t4-t3))

    return render(request, "ChartView/combinationlist.html", {"base":base, "form":form, "CombinationList":CombinationList})

def DetailView(request):
    form = ChartForm()

    #クエリの存在チェック
    ExistsPartsField = 'PartsField' in request.GET and request.GET.get('PartsField') !=''
    ExistsHiddenPartsField = 'HiddenPartsField' in request.GET and request.GET.get('HiddenPartsField') !=''
    ExistsUnitField  = 'UnitField' in request.GET and request.GET.get('UnitField') !=''

    if not(ExistsPartsField or ExistsUnitField or ExistsHiddenPartsField):
    #クエリの指定が存在しない場合
        ChartForm.MS1 = {\
        'Lv99Armor':0,\
        'Lv99MeleeATK':0,\
        'Lv99ShotATK':0,\
        'Lv99MeleeDEF':0,\
        'Lv99ShotDEF':0,\
        'Lv99BeamRES':0,\
        'Lv99PhysRES':0,\
    }
        form.MSAverage = ChartForm.MS1
        form.MSStdDev = ChartForm.MS1
        ShowcaseTweet = ''
        PrebanCode = ''
        PrebanName = ''
        GundamwikiName = ''
        GundamwikiIntro = ''

        return render(request, "ChartView/detail.html", {"base": base, "form": form, "MSAverage": form.MSAverage, "MSStdDev":form.MSStdDev,\
            "ShowcaseTweet":ShowcaseTweet, "PrebanCode":PrebanCode, "PrebanName":PrebanName, "GundamwikiName":GundamwikiName, "GundamwikiIntro":GundamwikiIntro})

    if ExistsPartsField or ExistsHiddenPartsField:
        PartsID = request.GET.get('HiddenPartsField') if ExistsHiddenPartsField else request.GET.get('PartsField')
        #https://yk5656.hatenablog.com/entry/20210410/1617980400
        ParentUnit = Unit.objects.filter(pk=Status.objects.get(pk=PartsID).Unit_id).first()
        UnitID = ParentUnit.id if ParentUnit is not None else ''

        form.MS1 = Status.objects.get(pk=PartsID)

        CategoryList = [form.MS1.Category, form.MS1.CombinedCategory]
        PartsCategoryList = makeCategoryList(CategoryList)
        print(PartsCategoryList)
        #平均、標準偏差の設定
        form.MSAverage, form.MSStdDev = getStatics(PartsCategoryList)

        #ワードタグの取得
        form.WordtagCount = [Status.objects.get(pk=PartsID).Wordtag1, Status.objects.get(pk=PartsID).Wordtag2]
        
    elif ExistsUnitField:
        PartsID = ''
        UnitID = request.GET.get('UnitField')

        CategoryList = list(Status.objects.filter(Unit__id=UnitID, Category__in=["Head", "Body", "Arms", "Legs", "Back"]).values_list("Category", flat=True))
        CombinedCategoryList = list(Status.objects.filter(Unit__id=UnitID, Category__in=["Head", "Body", "Arms", "Legs", "Back"]).values_list("CombinedCategory", flat=True))
        CategoryList.extend(CombinedCategoryList)

        UnitCategoryList = makeCategoryList(CategoryList)

        form.MS1 = getpartswithoutweaponshield(UnitID, UnitCategoryList)
        #注：Attributeを「追加」
        form.MS1["Attribute"] = Unit.objects.get(pk=UnitID).Attribute
        form.MS1["id"] = UnitID

        #平均、標準偏差を計算
        form.MSAverage, form.MSStdDev = getStatics(UnitCategoryList)
    
        #ワードタグの取得
        form.WordtagCount = {}
        WordtagList = list(Status.objects.filter(Unit_id=UnitID).values_list("Wordtag1", flat=True)) \
        + list(Status.objects.filter(Unit_id=UnitID).values_list("Wordtag2", flat=True))

        for CurrentWordtag in list(set(WordtagList)):
            form.WordtagCount[CurrentWordtag] = WordtagList.count(CurrentWordtag)
        #値順でソートしたい

    getAnotherAttribute(form, UnitID, PartsID)

    #セレクトボックスの初期値、絞り込み設定
    form.fields['UnitField'].initial = UnitID
    form.fields['PartsField'].initial = PartsID
    form.fields['PartsField'].queryset = Status.objects.filter(Unit_id=UnitID) if UnitID else Status.objects.all()

    #グラフの変更も必要なので、ボタンの状況はJS側でまとめて取得/設定したほうがいい。

    #紹介ツイートの設定
    if UnitID =='':
        ShowcaseTweet = ''
        PrebanCode = ''
        PrebanName = ''
        GundamwikiName = ''
        GundamwikiIntro = ''
    elif '【改造' in Unit.objects.get(pk=UnitID).MSName:
    #改造済の場合は元パーツから表示
        target = '】'
        idx = Unit.objects.get(pk=UnitID).MSName.find(target)
        MSNameBeforeAlter = Unit.objects.get(pk=UnitID).MSName[idx+1:]

        ShowcaseTweet = Unit.objects.get(MSName=MSNameBeforeAlter, Attribute=Unit.objects.get(pk=UnitID).Attribute).ShowcaseTweet
        PrebanCode = Unit.objects.get(MSName=MSNameBeforeAlter, Attribute=Unit.objects.get(pk=UnitID).Attribute).PrebanCode
        PrebanName = Unit.objects.get(MSName=MSNameBeforeAlter, Attribute=Unit.objects.get(pk=UnitID).Attribute).PrebanName
        GundamwikiName = Unit.objects.get(MSName=MSNameBeforeAlter, Attribute=Unit.objects.get(pk=UnitID).Attribute).GundamwikiName
        GundamwikiIntro = Unit.objects.get(MSName=MSNameBeforeAlter, Attribute=Unit.objects.get(pk=UnitID).Attribute).GundamwikiIntro
        
    else:
        
        ShowcaseTweet = Unit.objects.get(pk=UnitID).ShowcaseTweet
        PrebanCode = Unit.objects.get(pk=UnitID).PrebanCode
        PrebanName = Unit.objects.get(pk=UnitID).PrebanName
        GundamwikiName = Unit.objects.get(pk=UnitID).GundamwikiName
        GundamwikiIntro = Unit.objects.get(pk=UnitID).GundamwikiIntro

    return render(request, "ChartView/detail.html", {"base": base, "form":form, "MSAverage":form.MSAverage, "MSStdDev":form.MSStdDev,\
        "ShowcaseTweet":ShowcaseTweet, "PrebanCode":PrebanCode, "PrebanName":PrebanName, "GundamwikiName":GundamwikiName, "GundamwikiIntro":GundamwikiIntro})
    #formsは一度、viewsは都度計算
    #viewsで統計値を毎回出すと重くなる
    #特殊パターン(一体型、イレギュラーなUnit)以外の時は、あらかじめformsで計算しておく？


def getpartswithoutweaponshield(UnitID, UnitCategoryList):
#UnitIDに対応する頭～背の合計を取得
    key = ["Lv99Armor", "Lv99MeleeATK", "Lv99ShotATK", "Lv99MeleeDEF", "Lv99ShotDEF", "Lv99BeamRES", "Lv99PhysRES"]

    NPStatusArray = np.array([0,0,0,0,0,0,0])
    for Category in UnitCategoryList:
        NPStatusArray = NPStatusArray + getpartsstatus(UnitID, Category)

    return dict(zip(key, NPStatusArray))

def getpartsstatus(UnitID, SelectedCategory):
#UnitID, SelectedCategoryに対応するステータスを取得
    querySet = Status.objects.filter(Unit_id=UnitID, Category=SelectedCategory).first()
    #https://qiita.com/kkk_xiv/items/fd28514ed34be4c5b0f5
    if querySet is None:
        querysetstatus = np.array([0,0,0,0,0,0,0])
    else:
        querysetstatus = np.array([querySet.Lv99Armor,querySet.Lv99MeleeATK,querySet.Lv99ShotATK,querySet.Lv99MeleeDEF,querySet.Lv99ShotDEF,querySet.Lv99BeamRES,querySet.Lv99PhysRES])

    return querysetstatus

def BatchCompensation(ParentUnit):
    #不使用
    #証補正
    #https://qiita.com/hasegit/items/2cf05de74680717f9010
    batchcompensationlist = {\
    '5':1+0.45*2,\
    '4':1+0.45*2,\
    '3':1+0.45*3,\
    '2':1+0.45*4,\
    '1':1+0.45*5,       
    }

    batchcompensation = batchcompensationlist.get(str(ParentUnit.Rarity)) if ParentUnit is not None else 1
    return batchcompensation

    # djangoでcaptcha(問い合わせフォーム) https://sleepless-se.net/2021/06/19/how-to-setup-recaptcha-in-django/

def Traits1Filter(TraitObject, EffectKeyword, DictTraitOption):
    if EffectKeyword[0] == "時":
        trait1filter =\
            TraitObject.filter(\
                Q(Traits1Name__icontains="時"+EffectKeyword[1:])|\
                Q(Traits1Name__icontains="パーツの"+EffectKeyword[1:])|\
                Q(Traits1Name__icontains="武器の"+EffectKeyword[1:])|\
                Q(Traits1Name__icontains="し"+EffectKeyword[1:])|\
                Q(Traits1Name__icontains="後"+EffectKeyword[1:])|\
                Q(Traits1Name__icontains="間"+EffectKeyword[1:])|\
                # 条件なしを含みつつ、デメリット側(射撃攻撃の威力が〇%減少し～)を除外
                Q(Traits1Name__istartswith=EffectKeyword[1:]), ~Q(Traits1Name__istartswith=EffectKeyword[1:]+"が")\
            )
    else:
        trait1filter = TraitObject.filter(Traits1Name__icontains=EffectKeyword)

    AttributeList = ['Power','Technique','Speed']
    ExcludeAttributeList = AttributeList
    if DictTraitOption['TraitAttribute']:
        #3属性から指定した属性を除外したリスト(ExcludeAttributeList)を作る
        ExcludeAttributeList.remove(DictTraitOption['TraitAttribute'])

        #ExcludeAttributeListで指定した属性が条件のものを除外する
        for ExcludeAttribute in ExcludeAttributeList:
            trait1filter = trait1filter.filter(~Q(Traits1Name__icontains='自機の属性が'+ExcludeAttribute+'の時'),~Q(Traits1Name__icontains='小隊3機全てが'+ExcludeAttribute+'の時'))

    WordTagList = list(WordTag.objects.all().values_list("DisplayName", flat=True))
    ExcludeWordTagList = WordTagList

    existsExcludeWordTag = False
    for notExcludeWordTag in DictTraitOption['TraitWordtag']:
        if notExcludeWordTag:
            #全ワードタグから指定したワードタグを除外したリスト(ExcludeWordTagList)を作る
            ExcludeWordTagList.remove(notExcludeWordTag)
            existsExcludeWordTag = True

    if existsExcludeWordTag:
        #ExcludeWordTagListで指定したワードタグが条件のものを除外する
        for ExcludeWordTag in ExcludeWordTagList:
            trait1filter = trait1filter.filter(~Q(Traits1Name__icontains='自機が《'+ExcludeWordTag+'》の時'))

    if DictTraitOption['isArenaTraits']:
        trait1filter = trait1filter.filter(\
            ~Q(Traits1Name__icontains='秒後'),
            ~Q(Traits1Name__icontains='撃墜した時'),
            ~Q(Traits1Name__icontains='撃墜された時'),
            ~Q(Traits1Name__icontains='攻撃を受けた後'),
            ~Q(Q(Traits1Name__icontains='耐久力が'), Q(Traits1Name__icontains='以下の時'), ~Q(Traits1Name__icontains='以下の時耐久力が徐々に'))
            )

    if DictTraitOption['isSoloTraits']:
        trait1filter = trait1filter.filter(\
            ~Q(Traits1Name__icontains='小隊3機全てが'),
            ~Q(Traits1Name__icontains='小隊に全属性が揃っている時'),
            )

    return trait1filter

def Traits2Filter(TraitObject, EffectKeyword, DictTraitOption):
    if EffectKeyword[0] == "時":
        trait2filter =\
            TraitObject.filter(\
                Q(Traits2Name__icontains="時"+EffectKeyword[1:])|\
                Q(Traits2Name__icontains="パーツの"+EffectKeyword[1:])|\
                Q(Traits2Name__icontains="武器の"+EffectKeyword[1:])|\
                Q(Traits2Name__icontains="し"+EffectKeyword[1:])|\
                Q(Traits2Name__icontains="後"+EffectKeyword[1:])|\
                Q(Traits2Name__icontains="間"+EffectKeyword[1:])|\
                Q(Traits2Name__istartswith=EffectKeyword[1:]), ~Q(Traits2Name__istartswith=EffectKeyword[1:]+"が")\
            )
    else:
        trait2filter = TraitObject.filter(Traits2Name__icontains=EffectKeyword)

    AttributeList = ['Power','Technique','Speed']
    ExcludeAttributeList = AttributeList
    if DictTraitOption['TraitAttribute']:
        ExcludeAttributeList.remove(DictTraitOption['TraitAttribute'])

        for ExcludeAttribute in ExcludeAttributeList:
            trait2filter = trait2filter.filter(~Q(Traits2Name__icontains='自機の属性が'+ExcludeAttribute+'の時'),~Q(Traits2Name__icontains='小隊3機全てが'+ExcludeAttribute+'の時'))

    WordTagList = list(WordTag.objects.all().values_list("DisplayName", flat=True))
    ExcludeWordTagList = WordTagList

    existsExcludeWordTag = False
    for notExcludeWordTag in DictTraitOption['TraitWordtag']:
        if notExcludeWordTag:
            ExcludeWordTagList.remove(notExcludeWordTag)
            existsExcludeWordTag = True

    if existsExcludeWordTag:
        for ExcludeWordTag in ExcludeWordTagList:
            trait2filter = trait2filter.filter(~Q(Traits2Name__icontains='自機が《'+ExcludeWordTag+'》の時'))

    if DictTraitOption['isArenaTraits']:
        trait2filter = trait2filter.filter(\
            ~Q(Traits2Name__icontains='秒後'),
            ~Q(Traits2Name__icontains='撃墜した時'),
            ~Q(Traits2Name__icontains='撃墜された時'),
            ~Q(Traits2Name__icontains='攻撃を受けた後'),
            ~Q(Q(Traits2Name__icontains='耐久力が'), Q(Traits2Name__icontains='以下の時'), ~Q(Traits2Name__icontains='以下の時耐久力が徐々に'))
            )

    if DictTraitOption['isSoloTraits']:
        trait2filter = trait2filter.filter(\
            ~Q(Traits2Name__icontains='小隊3機全てが'),
            ~Q(Traits2Name__icontains='小隊に全属性が揃っている時'),
            )

    return trait2filter

def getAnotherAttribute(form, UnitID, PartsID):
    AttributeList = ["Speed", "Technique", "Power"]
    if PartsID == '':
        #機体の場合
        TargetUnit = Unit.objects.filter(pk=UnitID).first()
        NameforAnotherAttribute = []
        NameListbeforeAlter = []
        NameListafterAlter = []

        NameListbeforeAlter.append(excludealtertext(TargetUnit.MSName))

        NameListafterAlter.append("【改造】"+excludealtertext(TargetUnit.MSName))
        NameListafterAlter.append("【改造BIG】"+excludealtertext(TargetUnit.MSName))

        #改造前後のid取得
        if TargetUnit.MSName == excludealtertext(TargetUnit.MSName):
            #元機体が改造前の場合
            NameforAnotherAttribute = NameListbeforeAlter

            form.MS1["id_beforeAlter"] = UnitID

            QueryafterAlter = Unit.objects.filter(MSName__in=NameListafterAlter, Attribute=TargetUnit.Attribute).first()
            form.MS1["id_afterAlter"]  = QueryafterAlter.id if QueryafterAlter is not None else ''

        else:
            #元機体が改造後の場合
            NameforAnotherAttribute = NameListafterAlter

            QuerybeforeAlter = Unit.objects.filter(MSName__in=NameListbeforeAlter, Attribute=TargetUnit.Attribute).first()
            form.MS1["id_beforeAlter"]  = QuerybeforeAlter.id if QuerybeforeAlter is not None else ''

            form.MS1["id_afterAlter"] = UnitID

        #別属性のid取得
        for AnotherAttribute in AttributeList:
            QueryAnotherAttribute = Unit.objects.filter(MSName__in=NameforAnotherAttribute, Attribute=AnotherAttribute).first()
            form.MS1["id_"+ AnotherAttribute] = QueryAnotherAttribute.id if QueryAnotherAttribute is not None else ''

    else:
        #パーツの場合
        #すでに枠が存在しているため、form.MS1["AnotherAttribute_"+ AnotherAttribute]は使えない
        TargetStatus = Status.objects.filter(pk=PartsID).first()

        NameforAnotherAttribute = []
        NameListbeforeAlter = []
        NameListafterAlter = []

        NameListbeforeAlter.append(excludealtertext(TargetStatus.PartsName))

        NameListafterAlter.append("【改造】"+excludealtertext(TargetStatus.PartsName))
        NameListafterAlter.append("【改造BIG】"+excludealtertext(TargetStatus.PartsName))

        #改造前後のid取得
        if TargetStatus.PartsName == excludealtertext(TargetStatus.PartsName):
            #元パーツが改造前の場合
            NameforAnotherAttribute = NameListbeforeAlter

            #※パーツ側のみ、idにintをつける
            form.MS1.id_beforeAlter = int(PartsID)

            QueryafterAlter = Status.objects.filter(PartsName__in=NameListafterAlter, Category=TargetStatus.Category, Attribute=TargetStatus.Attribute).first()
            form.MS1.id_afterAlter  = int(QueryafterAlter.id) if QueryafterAlter is not None else ''

        else:
            #元パーツが改造後の場合
            NameforAnotherAttribute = NameListafterAlter

            QuerybeforeAlter = Status.objects.filter(PartsName__in=NameListbeforeAlter, Category=TargetStatus.Category, Attribute=TargetStatus.Attribute).first()
            form.MS1.id_beforeAlter  = int(QuerybeforeAlter.id) if QuerybeforeAlter is not None else ''

            form.MS1.id_afterAlter = int(PartsID)

        #別属性のid取得
        QueryAnotherAttribute = Status.objects.filter(PartsName__in=NameforAnotherAttribute, Category=TargetStatus.Category)

        QueryAnotherAttribute_Speed = QueryAnotherAttribute.filter(Attribute="Speed").first()
        form.MS1.id_Speed = QueryAnotherAttribute_Speed.id if QueryAnotherAttribute_Speed is not None else ''

        QueryAnotherAttribute_Technique = QueryAnotherAttribute.filter(Attribute="Technique").first()
        form.MS1.id_Technique = QueryAnotherAttribute_Technique.id if QueryAnotherAttribute_Technique is not None else ''

        QueryAnotherAttribute_Power = QueryAnotherAttribute.filter(Attribute="Power").first()
        form.MS1.id_Power = QueryAnotherAttribute_Power.id if QueryAnotherAttribute_Power is not None else ''

        #別属性のワードタグ
        if TargetStatus.MaxRarity == 7:
            if TargetStatus.Attribute != "Speed" and QueryAnotherAttribute_Speed is not None:
                form.MS1.Wordtag_Speed = [QueryAnotherAttribute_Speed.Wordtag1, QueryAnotherAttribute_Speed.Wordtag2]

            if TargetStatus.Attribute != "Technique" and QueryAnotherAttribute_Technique is not None:
                form.MS1.Wordtag_Technique = [QueryAnotherAttribute_Technique.Wordtag1, QueryAnotherAttribute_Technique.Wordtag2]

            if TargetStatus.Attribute != "Power" and QueryAnotherAttribute_Power is not None:
                form.MS1.Wordtag_Power = [QueryAnotherAttribute_Power.Wordtag1, QueryAnotherAttribute_Power.Wordtag2]

def excludealtertext(text):
    if '【改造' in text:
        target = '】'
        idx = text.find(target)
        text = text[idx+1:]
    return text    

def WordtagFilter(StatusList, Wordtag, includeSubWordtag):
    if includeSubWordtag:
    #rawsqlで対処
        subWordtagidList = []
        #Wordtagが正規のものかチェック(sqlinjection対策)
        WordtagCheck = WordTag.objects.filter(DisplayName=Wordtag).first()
        if WordtagCheck is not None:
            sql = "\
                SELECT Main.* FROM Chartview_Status as Main \
                    INNER JOIN Chartview_Status as Sub \
                        ON (Main.PartsName = Sub.PartsName \
                        OR Main.PartsName = '【改造】' || Sub.PartsName \
                        OR Main.PartsName = '【改造BIG】' || Sub.PartsName) \
                        AND Main.Category = Sub.Category \
                    WHERE (Main.Wordtag1 <> '"+Wordtag+"' AND Main.Wordtag2 <> '"+Wordtag+"' ) \
                    AND (Sub.Wordtag1 = '"+Wordtag+"' OR Sub.Wordtag2 = '"+Wordtag+"' ) \
                    AND  Main.MaxRarity=7 "
            #改造BIGの考慮
            # params = {"Wordtag1": "'"+Wordtag+"'"}
            subWordtagRawQuerySet = StatusList.raw(sql)
            #QuerysetとRawQuerysetで型が異なるため、idのリスト(subWordtagidList)を作ってStatusListでfilter
            for subWordtag in subWordtagRawQuerySet:
                subWordtagidList.append(subWordtag.id)

        #通常のワードタグ+subWordtagidListでフィルタ
        StatusList = StatusList.filter(Q(Wordtag1=Wordtag)|Q(Wordtag2=Wordtag)|Q(id__in=subWordtagidList))
    else:
        StatusList = StatusList.filter(Q(Wordtag1=Wordtag)|Q(Wordtag2=Wordtag))
    
    return StatusList

def getStatics(CategoryList):
    t3 = time.time()
    cursor = connection.cursor()
    inputquery = """
        SELECT
            SUM(Lv99Armor) as SUMLv99Armor,
            SUM(Lv99MeleeATK) as SUMLv99MeleeATK,
            SUM(Lv99ShotATK) as SUMLv99ShotATK,
            SUM(Lv99MeleeDEF) as SUMLv99MeleeDEF,
            SUM(Lv99ShotDEF) as SUMLv99ShotDEF,
            SUM(Lv99PhysRES) as SUMLv99PhysRES,
            SUM(Lv99BeamRES) as SUMLv99BeamRES,
            
            AVG(Lv99Armor) as AVGLv99Armor,
            AVG(Lv99MeleeATK) as AVGLv99MeleeATK,
            AVG(Lv99ShotATK) as AVGLv99ShotATK,
            AVG(Lv99MeleeDEF) as AVGLv99MeleeDEF,
            AVG(Lv99ShotDEF) as AVGLv99ShotDEF,
            AVG(Lv99PhysRES) as AVGLv99PhysRES,
            AVG(Lv99BeamRES) as AVGLv99BeamRES,
            
            AVG(Lv99Armor*Lv99Armor) as SQAVGLv99Armor,
            AVG(Lv99MeleeATK*Lv99MeleeATK) as SQAVGLv99MeleeATK,
            AVG(Lv99ShotATK*Lv99ShotATK) as SQAVGLv99ShotATK,
            AVG(Lv99MeleeDEF*Lv99MeleeDEF) as SQAVGLv99MeleeDEF,
            AVG(Lv99ShotDEF*Lv99ShotDEF) as SQAVGLv99ShotDEF,
            AVG(Lv99PhysRES*Lv99PhysRES) as SQAVGLv99PhysRES,
            AVG(Lv99BeamRES*Lv99BeamRES) as SQAVGLv99BeamRES     
        FROM
            Replacekeyword1
        Replacekeyword3
    """
    outputquery= listloop(inputquery, len(CategoryList)-1,CategoryList)

    cursor.execute(outputquery)
    CalcStatics = cursor.fetchall()
    t4 = time.time()
    print("rawsql:"+str(t4-t3))
    # print(outputquery)

    NPUnitSum = np.array(CalcStatics[0][:7])
    NPUnitAvg = np.array(CalcStatics[0][7:14])
    NPUnitSquareAvg = np.array(CalcStatics[0][14:])
    NPUnitStdDev = np.sqrt(NPUnitSquareAvg - np.square(NPUnitAvg))

    #辞書配列に格納する
    UnitAverage = {
        'Lv99Armor': NPUnitAvg[0],\
        'Lv99MeleeATK': NPUnitAvg[1],\
        'Lv99ShotATK': NPUnitAvg[2],\
        'Lv99MeleeDEF': NPUnitAvg[3],\
        'Lv99ShotDEF': NPUnitAvg[4],\
        'Lv99BeamRES': NPUnitAvg[5],\
        'Lv99PhysRES': NPUnitAvg[6],\
    }
    UnitStdDev = {
        'Lv99Armor': NPUnitStdDev[0],\
        'Lv99MeleeATK': NPUnitStdDev[1],\
        'Lv99ShotATK': NPUnitStdDev[2],\
        'Lv99MeleeDEF': NPUnitStdDev[3],\
        'Lv99ShotDEF': NPUnitStdDev[4],\
        'Lv99BeamRES': NPUnitStdDev[5],\
        'Lv99PhysRES': NPUnitStdDev[6],\
    }

    return UnitAverage, UnitStdDev

def listloop(inputquery, index, list):
    query=inputquery

    if index==0:
        Replacekeyword2 = """
            AND Sub.Category IN (''
        """

        if list[index] == "MELEE_WEAPON":
            Categorylist = MELEE_WEAPON
        elif list[index] == "SHOT_WEAPON":
            Categorylist = SHOT_WEAPON
        else:
            Categorylist = []
            Categorylist.append(list[index])

        for Category in Categorylist:
            Replacekeyword2 = Replacekeyword2 + ", '"+Category+"'"

        Replacekeyword2 = Replacekeyword2+"""
            )
            AND (Sub.CombinedCategory IS NULL OR Sub.CombinedCategory ='')
        """

        Replacekeyword3 = """
            WHERE Category IN (''
        """

        if list[index] == "MELEE_WEAPON":
            Categorylist = MELEE_WEAPON
        elif list[index] == "SHOT_WEAPON":
            Categorylist = SHOT_WEAPON
        else:
            Categorylist = []
            Categorylist.append(list[index])

        for Category in Categorylist:
            Replacekeyword3 = Replacekeyword3 + ", '"+Category+"'"

        Replacekeyword3 = Replacekeyword3+"""
            )
            AND (CombinedCategory IS NULL OR CombinedCategory ='')
        """

        query=query.replace("Replacekeyword1", "Chartview_Status")
        query=query.replace("Replacekeyword2", Replacekeyword2)
        query=query.replace("Replacekeyword3", Replacekeyword3)

        return query

    Replacekeyword1 = """
            (
                SELECT
                    Main.Unit_id,
                    Main.Lv99Armor + Sub.Lv99Armor as Lv99Armor, 
                    Main.Lv99MeleeATK + Sub.Lv99MeleeATK as Lv99MeleeATK, 
                    Main.Lv99ShotATK + Sub.Lv99ShotATK as Lv99ShotATK, 
                    Main.Lv99MeleeDEF + Sub.Lv99MeleeDEF as Lv99MeleeDEF, 
                    Main.Lv99ShotDEF + Sub.Lv99ShotDEF as Lv99ShotDEF, 
                    Main.Lv99PhysRES + Sub.Lv99PhysRES as Lv99PhysRES, 
                    Main.Lv99BeamRES + Sub.Lv99BeamRES as Lv99BeamRES
                from
                    Chartview_Status AS Main
                INNER JOIN 
                    Replacekeyword1 AS Sub
                ON
                    Main.Unit_id = Sub.Unit_id
                WHERE 
                    Main.Category IN (''
    """

    if list[index] == "MELEE_WEAPON":
        Categorylist = MELEE_WEAPON
    elif list[index] == "SHOT_WEAPON":
        Categorylist = SHOT_WEAPON
    else:
        Categorylist = []
        Categorylist.append(list[index])

    for Category in Categorylist:
        Replacekeyword1 = Replacekeyword1 + ", '"+Category+"'"

    Replacekeyword1 = Replacekeyword1+"""
                )
                AND (Main.CombinedCategory IS NULL OR Main.CombinedCategory ='')
                Replacekeyword2
            )   
    """
    query=query.replace("Replacekeyword2", "")
    query=query.replace("Replacekeyword3", "")
    query=query.replace("Replacekeyword1", Replacekeyword1)

    return listloop(query, index-1, list)


def makeCategoryList(CategoryList):
    outputCategoryList = []

    for index, Category in enumerate(CategoryList):
        if Category in MELEE_WEAPON:
            outputCategoryList.append("MELEE_WEAPON")
        elif Category in SHOT_WEAPON:
            outputCategoryList.append("SHOT_WEAPON")
        else:
            outputCategoryList.append(CategoryList[index])

    # list(set())で重複削除
    CategoryList=list(set(CategoryList))

    #Noneや''の削除
    CategoryList = list(filter(None, CategoryList))

    # https://www.delftstack.com/ja/howto/python/remove-duplicates-from-list-python/
    return CategoryList

def calcStatusCombination():
    print("aaa");

