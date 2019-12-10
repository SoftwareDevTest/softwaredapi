import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from rest_framework.views import APIView

from pyecharts.charts import Bar, Pie
from pyecharts import options as opts

from interface.models import ProductInfo, ModuleInfo, CaseGroupInfo, InterfaceInfo


def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


JsonResponse = json_response
JsonError = json_error

product_count = ProductInfo.objects.all().count()
module_count = ModuleInfo.objects.all().count()
case_group_count = CaseGroupInfo.objects.all().count()
total = InterfaceInfo.objects.all().count()
success = InterfaceInfo.objects.filter(pass_status=1).count()
fail = InterfaceInfo.objects.filter(pass_status=0).count()
not_run = InterfaceInfo.objects.filter(pass_status=None).count()


def bar_base() -> Bar:
    c = (
        Bar()
        .add_xaxis(["产品线", "模块", "用例组", "用例"])
        .add_yaxis("总共", [product_count, module_count, case_group_count, total])
        .add_yaxis("通过", ["", "", "", success])
        .add_yaxis("不通过", ["", "", "", fail])
        .add_yaxis("未运行", ["", "", "", not_run])
        .set_colors(["blue", "green", "red", "purple"])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="接口测试报告_柱状图"),
            yaxis_opts=opts.AxisOpts(name="Y轴（数量）"),
            xaxis_opts=opts.AxisOpts(name="X轴（模块）"),
            toolbox_opts=opts.ToolboxOpts()
        )
        .set_series_opts(
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                    opts.MarkPointItem(type_="min", name="最小值"),
                    opts.MarkPointItem(type_="average", name="平均值"),
                ]
            ),
        )
        .dump_options_with_quotes()
    )
    return c


def pie_base() -> Pie:
    v1 = ["通过", "不通过", "未运行"]
    v2 = [success, fail, not_run]

    c = (
        Pie()
        .add(
            "",
            [list(z) for z in zip(v1, v2)],
            radius=["40%", "60%"],
            label_opts=opts.LabelOpts(
                position="outside",
                formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}  ",
                background_color="#eee",
                border_color="#aaa",
                border_width=1,
                border_radius=4,
                rich={
                    "a": {"color": "#999", "lineHeight": 22, "align": "center"},
                    "abg": {
                        "backgroundColor": "#e3e3e3",
                        "width": "100%",
                        "align": "right",
                        "height": 22,
                        "borderRadius": [4, 4, 0, 0],
                    },
                    "hr": {
                        "borderColor": "#aaa",
                        "width": "100%",
                        "borderWidth": 0.5,
                        "height": 0,
                    },
                    "b": {"fontSize": 16, "lineHeight": 33},
                    "per": {
                        "color": "#eee",
                        "backgroundColor": "#334455",
                        "padding": [2, 4],
                        "borderRadius": 2,
                    },
                },
            ),
        )
        .set_colors(["green", "red", "purple"])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="接口测试报告_饼状图"),
            toolbox_opts=opts.ToolboxOpts()
        )
        .dump_options_with_quotes()
    )
    return c


class BarChartView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(bar_base()))


class PieBarChartView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(pie_base()))


class IndexView(LoginRequiredMixin, APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(
            content=open("interface/templates/index.html").read())
