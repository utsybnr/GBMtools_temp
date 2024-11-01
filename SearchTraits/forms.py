from django import forms, db
from django.db import connection
from django.db.models import Q

from . import models

from Chartview.models import Status, Unit
import numpy as np
import pandas as pd
import time

#セレクトボックスでDisplayNameだけ表示するためのclass
class DispChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, table):
        return table.DisplayName

class AttributeChoices(db.models.TextChoices):
    #https://yu-nix.com/blog/2021/8/18/django-choicefield/
    NoAttribute = '', '--------'
    Speed = 'Speed', 'Speed'
    Technique = 'Technique', 'Technique'
    Power = 'Power', 'Power'

class StatusTypeChoices(db.models.TextChoices):
    Armor = 'Armor', 'Armor'
    MeleeATK = 'MeleeATK', 'MeleeATK'
    ShotATK = 'ShotATK', 'ShotATK'
    MeleeDEF = 'MeleeDEF', 'MeleeDEF'
    ShotDEF = 'ShotDEF', 'ShotDEF'
    BeamRES = 'BeamRES', 'BeamRES'
    PhysRES = 'PhysRES', 'PhysRES'

class CategoryChoices(db.models.TextChoices):
    Head = 'Head', 'Head'
    Body = 'Body', 'Body'
    Arms = 'Arms', 'Arms'
    Legs = 'Legs', 'Legs'
    Back = 'Back', 'Back'
    Shield = 'Shield', 'Shield'
    ShotWeapon = 'ShotWeapon', 'ShotWeapon'
    MeleeWeapon = 'MeleeWeapon', 'MeleeWeapon'
    AI = 'AI', 'AI'

class JoblisenceChoices(db.models.TextChoices):
    AllJoblisence = '', '--------'
    Defender = 'Defender', 'Defender'
    In_Fighter = 'In-Fighter', 'In-Fighter'
    Out_Fighter = 'Out-Fighter', 'Out-Fighter'
    Middle_Shooter = 'Middle-Shooter', 'Middle-Shooter'
    Long_Shooter = 'Long-Shooter', 'Long-Shooter'
    Supporter = 'Supporter', 'Supporter'

class MeleeWeaponChoices(db.models.TextChoices):
    AllMeleeWeapon = '', '--------'
    Saber = 'サーベル', 'サーベル'
    DoubleSaber = 'ダブルサーベル', 'ダブルサーベル'
    Axe = 'アックス', 'アックス'
    Sword = '大剣', '大剣'
    Lance = 'ランス', 'ランス'
    Module = 'モジュール', 'モジュール'
    Whip = 'ムチ', 'ムチ'
    TwinBlade = 'ツインブレード', 'ツインブレード'

class ShotWeaponChoices(db.models.TextChoices):
    AllShotWeapon = '', '--------'
    Rifle = 'ライフル', 'ライフル'
    LongRifle = 'ロングライフル', 'ロングライフル'
    DoubleRifle = 'ダブルライフル', 'ダブルライフル'
    MachineGun = 'マシンガン', 'マシンガン'
    Bazooka = 'バズーカ', 'バズーカ'
    GatilngGun = 'ガトリングガン', 'ガトリングガン'

class AIDistanceChoices(db.models.TextChoices):
    NoAIDistance = '', '--------'
    Short = '近距離', '近距離'
    Mid = '中距離', '中距離'
    Long = '遠距離', '遠距離'

class AITypeChoices(db.models.TextChoices):
    NoAIType = '', '--------'
    Support = '支援', '支援'
    Balance = 'バランス', 'バランス'
    Independent = '独立', '独立'

class SearchForm(forms.Form):
    Attribute = forms.ChoiceField(
        label='パーツ属性',
        required=False,
        disabled=False,
        choices=AttributeChoices.choices,
        widget=forms.widgets.Select(attrs={'id':'Attribute',}),
    )

    Wordtag1 = DispChoiceField(
        queryset = models.WordTag.objects.all().order_by("Order"),
        label='ワードタグ1', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'Wordtag1', 'name': 'Wordtag1','class':'select_short',}),
        to_field_name='DisplayName'
        )

    Wordtag2 = DispChoiceField(
        queryset = models.WordTag.objects.all().order_by("Order"),
        label='ワードタグ2', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'Wordtag2', 'name': 'Wordtag2','class':'select_short',}),
        to_field_name='DisplayName'
        )

    includeSubWordtag = forms.CharField(
        label='★7は別属性のタグも含む',
        required=False,
        disabled=False,
        widget=forms.CheckboxInput(attrs={'id': 'includeSubWordtag', 'name': 'includeSubWordtag',})
    )
    
    EffectFilter1 = DispChoiceField(
        queryset = models.EffectFilter.objects.all().order_by("Order"),
        label='効果フィルタ1', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'EffectFilter1' ,'name': 'EffectFilter1', 'class':'select_short',}))

    Effect1 = DispChoiceField(
        queryset = models.Effect.objects.all().order_by("FilterID", "Order"),
        label='効果1', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'Effect1', 'name': 'Effect1', 'class':'select_short',}),
        to_field_name='Query')

    EffectFilter2 = DispChoiceField(
        queryset = models.EffectFilter.objects.all().order_by("Order"),
        label='効果フィルタ2', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'EffectFilter2' ,'name': 'EffectFilter2', 'class':'select_short',}))

    Effect2 = DispChoiceField(
        queryset = models.Effect.objects.all().order_by("FilterID", "Order"),
        label='効果2', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'Effect2', 'name': 'Effect2', 'class':'select_short',}),
        to_field_name='Query')

    TraitAttribute = forms.ChoiceField(
        label='特性を発動可能な属性',
        required=False,
        disabled=False,
        choices=AttributeChoices.choices,
        widget=forms.widgets.Select(attrs={'id':'TraitAttribute', 'class':'select_short',}),
    )

    TraitWordtag1 = DispChoiceField(
        queryset = models.WordTag.objects.all().order_by("Order"),
        label='特性を発動可能なワードタグ1', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'TraitWordtag1', 'name': 'TraitWordtag1'}),
        to_field_name='DisplayName'
        )

    TraitWordtag2 = DispChoiceField(
        queryset = models.WordTag.objects.all().order_by("Order"),
        label='特性を発動可能なワードタグ2', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'TraitWordtag2', 'name': 'TraitWordtag2',}),
        to_field_name='DisplayName'
        )

    TraitWordtag3 = DispChoiceField(
        queryset = models.WordTag.objects.all().order_by("Order"),
        label='特性を発動可能なワードタグ3', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'TraitWordtag3', 'name': 'TraitWordtag3',}),
        to_field_name='DisplayName'
        )

    isArenaTraits = forms.CharField(
        label='即発動が不可の特性を除外する',
        required=False,
        disabled=False,
        widget=forms.CheckboxInput(attrs={'id': 'isArenaTraits', 'name': 'isArenaTraits',})
    )

    isSoloTraits = forms.CharField(
        label='小隊が必要な特性を除外する',
        required=False,
        disabled=False,
        widget=forms.CheckboxInput(attrs={'id': 'isSoloTraits', 'name': 'isSoloTraits',})
    )

    AIDistance = forms.ChoiceField(
        label='AIタイプ(距離)',
        required=False,
        disabled=False,
        choices=AIDistanceChoices.choices,
        widget=forms.widgets.Select(attrs={'id':'AIDistance', 'class':'select_short',}),
    )

    AIType = forms.ChoiceField(
        label='AIタイプ(型)',
        required=False,
        disabled=False,
        choices=AITypeChoices.choices,
        widget=forms.widgets.Select(attrs={'id':'AIType', 'class':'select_short',}),
    )

    SelectStatusType = forms.ChoiceField(
        label='ステータス選択',
        required=False,
        disabled=False,
        choices=StatusTypeChoices.choices,
        widget=forms.widgets.Select(attrs={'class':'form-select', 'id':'SelectStatusType', 'name':'SelectStatusType'}),
    )

    SelectCategory = forms.ChoiceField(
        label='部位選択',
        required=False,
        disabled=False,
        choices=CategoryChoices.choices,
        widget=forms.widgets.Select(attrs={'class':'form-select', 'id':'SelectCategory', 'name':'SelectCategory'}),
    )

    MeleeWeapon = forms.ChoiceField(
        label='部位選択詳細：格闘武器',
        required=False,
        disabled=False,
        choices=MeleeWeaponChoices.choices,
        widget=forms.widgets.Select(attrs={'id':'MeleeWeapon', 'class':'form-select',}),
    )
    
    ShotWeapon = forms.ChoiceField(
        label='部位選択詳細：射撃武器',
        required=False,
        disabled=False,
        choices=ShotWeaponChoices.choices,
        widget=forms.widgets.Select(attrs={'id':'ShotWeapon', 'class':'form-select',}),
    )

    Joblisence = forms.ChoiceField(
        label='ジョブライセンス',
        required=False,
        disabled=False,
        choices=JoblisenceChoices.choices,
        widget=forms.widgets.Select(attrs={'id':'Joblisence', 'class':'form-select',}),
    )

    isAlter = forms.CharField(
        label='改造パーツ以外の有無',
        required=False,
        disabled=False,
        widget=forms.CheckboxInput(attrs={'class':'form-check-input', 'id': 'isAlter', 'name': 'isAlter',})
    )

    withGear = forms.CharField(
        label='ステータスのギア補正有無',
        required=False,
        disabled=False,
        widget=forms.CheckboxInput(attrs={'class':'form-check-input', 'id': 'withGear', 'name': 'withGear',})
    )

    withCombinedParts = forms.CharField(
        label='一体型パーツ有無',
        required=False,
        disabled=False,
        widget=forms.CheckboxInput(attrs={'class':'form-check-input', 'id': 'withCombinedParts', 'name': 'withCombinedParts',})
    )

class SearchForm_2021Ver(forms.Form):
    ConditionFilter = DispChoiceField(
        queryset = models.ConditionFilter.objects.all().order_by("Order"),
        label='条件フィルタ', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'ConditionFilter', 'class': 'selModalaaa',}))

    Condition = DispChoiceField(
        queryset = models.Condition.objects.all().order_by("FilterID", "Order"),
        label='条件', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'Condition',}),
        to_field_name='Query')

    EffectFilter = DispChoiceField(
        queryset = models.EffectFilter.objects.all().order_by("Order"),
        label='効果フィルタ', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'EffectFilter' ,'name': 'EffectFilter',}))

    Effect = DispChoiceField(
        queryset = models.Effect.objects.all().order_by("FilterID", "Order"),
        label='効果', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'Effect', 'name': 'Effect',}),
        to_field_name='Query')

    Part = DispChoiceField(
        queryset = models.Part.objects.all().order_by("Order"),
        label='部位', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'Part', 'name': 'Part',}),
        to_field_name='Query')

    Wordtag1 = DispChoiceField(
        queryset = models.WordTag.objects.all().order_by("Order"),
        label='ワードタグ1', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'Wordtag1', 'name': 'Wordtag1',}),
        to_field_name='DisplayName'
        )

    Wordtag2 = DispChoiceField(
        queryset = models.WordTag.objects.all().order_by("Order"),
        label='ワードタグ2', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id': 'Wordtag2', 'name': 'Wordtag2',}),
        to_field_name='DisplayName'
        )

    isAlter = forms.CharField(
        label='改造パーツのみ',
        required=False,
        disabled=False,
        widget=forms.CheckboxInput(attrs={'id': 'isAlter', 'name': 'isAlter', 'value': '【改造',})
    )


class UnitChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, table):
        return table.MSName + "(" + table.Attribute + ")"

class PartsChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, table):
        CombinedCategory = '+' + table.CombinedCategory if table.CombinedCategory else ''
        Attribute = table.Attribute if table else ''
        return '【' + table.Category + CombinedCategory + '】' + table.PartsName + "(" + Attribute + ")"

class baseForm(forms.Form):
    UnitField = UnitChoiceField(
        queryset = Unit.objects.all().order_by('id').reverse(),
        label='機体名', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id':'Unit_base', 'class':'select2box', 'name':'query', 'onchange':'location.href="/search/detail?UnitField=" + this.value;', }))

class ChartForm(forms.Form):
    UnitField = UnitChoiceField(
        queryset = Unit.objects.all().order_by('id').reverse(),
        label='機体名', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id':'Unit', 'class':'select2box', 'name':'query', 'onchange':'submit(this.form);', }))

    PartsField = PartsChoiceField(
        queryset = Status.objects.all(),
        label='パーツ名', 
        required=False,
        disabled=False,
        widget=forms.Select(attrs={'id':'Parts', 'class':'select2box', 'onchange':'submit(this.form);',}))

    HiddenPartsField = forms.CharField(
        label='パーツ名(別機体のパーツに直接遷移する場合に利用)',
        required=False,
        disabled=False,
        max_length=100,
        widget=forms.HiddenInput(attrs={'id':'hdnParts',})
        )
                
    def CalcStaticsOld():
    # numpy+ORMで計算していた方法：SQLで直接計算したほうが軽いので現在未使用。
        ALLUnit = Unit.objects.all().values("id")
        arr = np.empty(0)
        for CurrentUnit in ALLUnit:
            querySet = Status.objects.filter(Unit_id=CurrentUnit["id"], Category="Arms").first()

            #腕がない場合or腕が一体型でない場合...?
            if querySet is None or querySet.CombinedCategory is None or querySet.CombinedCategory == "":
            #腕盾機体を除外
                arr = np.append(arr, getpartswithoutweaponshield(CurrentUnit["id"]), axis=0)

        arr = arr.reshape(-1, 7)
        NPUnitSum=np.sum(arr, axis=0)
        NPUnitAvg=np.mean(arr, axis=0)
        NPUnitSquareAvg=np.mean(np.square(arr), axis=0)

        def getpartswithoutweaponshield(UnitID):
        #UnitIDに対応する頭～背の合計を取得
            CategoryKey = ["Head", "Body", "Arms", "Legs", "Back"]
            UnitStatus = np.zeros(7)
            for CurrentCategory in CategoryKey:
                querySet = Status.objects.filter(Unit_id=UnitID, Category=CurrentCategory).first()
                #https://qiita.com/kkk_xiv/items/fd28514ed34be4c5b0f5
                if querySet is not None:
                    UnitStatus += np.array([querySet.Lv99Armor,querySet.Lv99MeleeATK,querySet.Lv99ShotATK,querySet.Lv99MeleeDEF,querySet.Lv99ShotDEF,querySet.Lv99BeamRES,querySet.Lv99PhysRES])

            return UnitStatus


    #cursorで算出(Raw query must include the primary keyのため、rawでは集計不可)
    # t3 = time.time()
    # cursor = connection.cursor()
    # #   --機体statusの集計\
    # #   		--腕が一体型でない機体の頭～BPのSUM(機体status)
    # #				    -- 腕が一体型でない機体
    # #                           -- 腕が一体型の機体のid
    # rawsql = """
    #     SELECT
    #         SUM(UnitLv99Armor) as SUMUnitLv99Armor,
    #         SUM(UnitLv99MeleeATK) as SUMUnitLv99MeleeATK,
    #         SUM(UnitLv99ShotATK) as SUMUnitLv99ShotATK,
    #         SUM(UnitLv99MeleeDEF) as SUMUnitLv99MeleeDEF,
    #         SUM(UnitLv99ShotDEF) as SUMUnitLv99ShotDEF,
    #         SUM(UnitLv99PhysRES) as SUMUnitLv99PhysRES,
    #         SUM(UnitLv99BeamRES) as SUMUnitLv99BeamRES,
            
    #         AVG(UnitLv99Armor) as AVGUnitLv99Armor,
    #         AVG(UnitLv99MeleeATK) as AVGUnitLv99MeleeATK,
    #         AVG(UnitLv99ShotATK) as AVGUnitLv99ShotATK,
    #         AVG(UnitLv99MeleeDEF) as AVGUnitLv99MeleeDEF,
    #         AVG(UnitLv99ShotDEF) as AVGUnitLv99ShotDEF,
    #         AVG(UnitLv99PhysRES) as AVGUnitLv99PhysRES,
    #         AVG(UnitLv99BeamRES) as AVGUnitLv99BeamRES,
            
    #         AVG(UnitLv99Armor*UnitLv99Armor) as SQAVGUnitLv99Armor,
    #         AVG(UnitLv99MeleeATK*UnitLv99MeleeATK) as SQAVGUnitLv99MeleeATK,
    #         AVG(UnitLv99ShotATK*UnitLv99ShotATK) as SQAVGUnitLv99ShotATK,
    #         AVG(UnitLv99MeleeDEF*UnitLv99MeleeDEF) as SQAVGUnitLv99MeleeDEF,
    #         AVG(UnitLv99ShotDEF*UnitLv99ShotDEF) as SQAVGUnitLv99ShotDEF,
    #         AVG(UnitLv99PhysRES*UnitLv99PhysRES) as SQAVGUnitLv99PhysRES,
    #         AVG(UnitLv99BeamRES*UnitLv99BeamRES) as SQAVGUnitLv99BeamRES
            
    #     FROM(
    #             SELECT
    #                 Chartview_Status.Unit_id,
    #                 SUM(Chartview_Status.Lv99Armor) as UnitLv99Armor,
    #                 SUM(Chartview_Status.Lv99MeleeATK) as UnitLv99MeleeATK,
    #                 SUM(Chartview_Status.Lv99ShotATK) as UnitLv99ShotATK,
    #                 SUM(Chartview_Status.Lv99MeleeDEF) as UnitLv99MeleeDEF,
    #                 SUM(Chartview_Status.Lv99ShotDEF) as UnitLv99ShotDEF,
    #                 SUM(Chartview_Status.Lv99PhysRES) as UnitLv99PhysRES,
    #                 SUM(Chartview_Status.Lv99BeamRES) as UnitLv99BeamRES
    #             from
    #                 Chartview_Status
    #                 inner join (
    #                     SELECT
    #                         Chartview_Unit.id
    #                     from
    #                         Chartview_Unit
    #                         LEFT JOIN (
    #                             SELECT
    #                                 DISTINCT Chartview_Status.Unit_id
    #                             FROM
    #                                 Chartview_Status
    #                                 INNER JOIN Chartview_Unit 
    #                                     ON Chartview_Status.Unit_id = Chartview_Unit.id
    #                             WHERE
    #                                 Chartview_Status.Category = 'Arms'
    #                                 and Chartview_Status.CombinedCategory IS NOT NULL
    #                                 and Chartview_Status.CombinedCategory <> ''
    #                         ) as CombinedArms 
    #                             ON Chartview_Unit.id = CombinedArms.Unit_id
    #                     WHERE
    #                         CombinedArms.Unit_id IS NULL
    #                 ) as notCombinedArmsUnit 
    #                     ON Chartview_Status.Unit_id = notCombinedArmsUnit.id
    #             WHERE
    #                 Chartview_Status.Category in ('Head', 'Body', 'Arms', 'Legs', 'Back')
    #             group by
    #                 Unit_id
    #         )
    #     """
    # cursor.execute(rawsql)
    # CalcStatics = cursor.fetchall()
    # t4 = time.time()
    # print("rawsql:"+str(t4-t3))
    # NPUnitSum = np.array(CalcStatics[0][:7])
    # NPUnitAvg = np.array(CalcStatics[0][7:14])
    # NPUnitSquareAvg = np.array(CalcStatics[0][14:])
    # NPUnitStdDev = np.sqrt(NPUnitSquareAvg - np.square(NPUnitAvg))

    # #辞書配列に格納する
    # UnitAverage = {
    #     'Lv99Armor': NPUnitAvg[0],\
    #     'Lv99MeleeATK': NPUnitAvg[1],\
    #     'Lv99ShotATK': NPUnitAvg[2],\
    #     'Lv99MeleeDEF': NPUnitAvg[3],\
    #     'Lv99ShotDEF': NPUnitAvg[4],\
    #     'Lv99BeamRES': NPUnitAvg[5],\
    #     'Lv99PhysRES': NPUnitAvg[6],\
    # }
    # UnitStdDev = {
    #     'Lv99Armor': NPUnitStdDev[0],\
    #     'Lv99MeleeATK': NPUnitStdDev[1],\
    #     'Lv99ShotATK': NPUnitStdDev[2],\
    #     'Lv99MeleeDEF': NPUnitStdDev[3],\
    #     'Lv99ShotDEF': NPUnitStdDev[4],\
    #     'Lv99BeamRES': NPUnitStdDev[5],\
    #     'Lv99PhysRES': NPUnitStdDev[6],\
    # }

    # MSAverage=UnitAverage
    # MSStdDev=UnitStdDev

    def calcStatusCombination():
        #組み合わせ計算
        PartsList = Status.objects.filter(Category='Head')
        WordtagDummyList, IsBigDummyList, MainPartsMatrix, SubPartsWithoutRateMatrix = [], [], np.zeros((PartsList.count(), PartsList.count())), np.zeros((PartsList.count(), PartsList.count()))
        AvailableWordtagList = list(models.WordTag.objects.all())
        for i, CurrentPart in enumerate(PartsList):
            #ワードタグを01配列に変換
            WordTag1OrderNum = models.WordTag.objects.get(DisplayName=CurrentPart.Wordtag1).Order
            WordTag2OrderNum = models.WordTag.objects.get(DisplayName=CurrentPart.Wordtag2).Order
            CurrentWordtagDummyList = np.zeros(26)
            CurrentWordtagDummyList[WordTag1OrderNum-1] = 1
            CurrentWordtagDummyList[WordTag2OrderNum-1] = 1
            WordtagDummyList.append(CurrentWordtagDummyList)

            #Big=1,それ以外-1で格納
            IsBigDummyList.append(1 if '【改造BIG】' in CurrentPart.PartsName else -1)

            #同名別パーツ、改造が考慮できていない
            #改造、属性情報は別の列にするor"】"や"（"でカットして、列ごとに判定
            #判定方法：同名用の別リストを作成？パーツ名のリストを用意し、置換：同名であれば3、それ以外は0

            #ワードタグとの兼ね合いをどうするか。→ ワードタグと同名の行列を加算し、3以上であれば3に置換とかできれば…(Bigを足す前にやる)

            #サブパーツのステータスを計算用行列に格納
            SubPartsWithoutRateMatrix[i][i] = CurrentPart.Lv99Armor

        PartsNameList = (list(PartsList.values_list("PartsName", flat=True)))
        #pandasならfor使わずに置換できる？
        pdPartsNameList = pd.DataFrame(PartsNameList)

        WordtagDummyList = np.array(WordtagDummyList)
        IsBigDummyList = np.array(IsBigDummyList)

        #メインパーツ加算用の行列
        #ベクトルはTで転置できないのでreshape https://note.nkmk.me/python-numpy-transpose/
        MainPartsMatrix = np.array(list(PartsList.values_list("Lv99Armor", flat=True))).reshape(-1,1)

        #リストに転置行列を乗じてワードタグ一致数を取得
        WordtagMatchList = np.dot(WordtagDummyList, WordtagDummyList.T)

        #同パーツ(=単位行列)+1 、スキルレベル分+0.5
        WordtagMatchList += np.eye(PartsList.count()) + 0.5
        WordtagMatchList = np.where( WordtagMatchList>3.5, 3.5, WordtagMatchList)

        #直積で同スケール=1, それ以外-1の行列ができる。-1して-1を乗ずることで、スケール違いの補正を算出。
        IsBigMatchList = (np.outer(IsBigDummyList.T, IsBigDummyList)-1)*-1
        #レートの算出
        SubPartsRateMatrix = (WordtagMatchList + IsBigMatchList)/10
        #パーツのステータスをかけて実際の値を算出
        SubPartsMatrix = np.dot(SubPartsRateMatrix, SubPartsWithoutRateMatrix)
        #print(SubPartsMatrix + MainPartsMatrix)


    #パーツごとの統計値
    #https://qiita.com/no-use-kuro/items/9c7c1b6dca07344cc76e

    # Average ={'Head':0,'Body':0,'Arms':0,'Legs':0,'Back':0}
    # for CurrentCategory in CategoryList:
    #     Average[CurrentCategory] = \
    #         Status.objects.filter(Category=CurrentCategory, CombinedCategory__isnull=True).aggregate(\
    #         Lv99Armor=Avg('Lv99Armor')\
    #         , Lv99MeleeATK=Avg('Lv99MeleeATK')\
    #         , Lv99ShotATK=Avg('Lv99ShotATK')\
    #         , Lv99MeleeDEF=Avg('Lv99MeleeDEF')\
    #         , Lv99ShotDEF=Avg('Lv99ShotDEF')\
    #         , Lv99BeamRES=Avg('Lv99BeamRES')\
    #         , Lv99PhysRES=Avg('Lv99PhysRES')\
    #         )    