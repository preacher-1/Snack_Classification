// 文件上传的间接调用
function button_click() {
    document.getElementById('image').click();
}

// 点击图片放大
function seeBigImage() {
    var modal = document.getElementById("myModal");
    var modalImg = document.getElementById("img01");
    var captionText = document.getElementById("caption");
    modal.style.display = "block";
    console.log($(this).attr('src'));
    modalImg.src = $(this).attr('src');
    captionText.innerHTML = $(this).attr('alt');
}

$(document).ready(function () {
    // 显示上传的图片文件
    document.getElementById('image').addEventListener('change', function (event) {
        var file = event.target.files[0];  // 获取上传的图片文件
        var imageType = /image.*/;  // 用于检查文件类型是否为图片

        if (file.type.match(imageType)) {
            var reader = new FileReader();  // 创建FileReader对象来读取文件

            reader.onload = function (e) {
                var img = new Image();  // 创建新的img元素来展示图片
                img.maxWidth = 200;  // 设置最大宽度为200像素
                img.src = e.target.result; // 通过FileReader读取的图片数据将直接作为图片的src

                var imagePreview = document.getElementById('imagePreview');
                imagePreview.innerHTML = '';  // 清空之前的预览
                imagePreview.appendChild(img);  // 在页面上显示上传的图片
            }

            reader.readAsDataURL(file);  // 读取文件并将其作为DataURL返回
        } else {
            alert('上传的文件不是图片类型！');
        }
    });
    // 点击提交按钮
    $('#upload-form').submit(function (event) {
        // 阻止默认提交事件
        event.preventDefault();
        var formdata = new FormData(), url;
        // 对于提供的信息形式，选择不同的处理方式
        if (this.image.files.length > 0) {
            url = 'preprocess/';
            formdata.append('data', this.image.files[0]);
        } else if (this.image_url.value !== '') {
            url = 'download/'
            formdata.append('data', this.image_url.value);
            $('#status').append('<div>从' + this.image_url.value + '下载图片...</div>');
            this.image_url.value = '';
        } else {
            alert('请选择图片或输入图片URL');
            return;
        }
        // 清空上一次提交的状态信息
        $('#status').empty();
        $('#response').empty();
        $('#result').empty();
        $('#imagePreview').empty();
        this.reset();

        $.ajax({
            url: url,
            type: 'POST',
            data: formdata,
            contentType: false,
            processData: false,
            success: function (response) {
                if (response.stat === 'download_complete') {
                    $('#status').append('<div>图片下载成功，已下载' + response.size + 'KB，用时' + response.used_time + '秒。</div>');
                    process(response.img_path);
                } else if (response.stat === 'preprocess_complete') {
                    $('#status').append('<div>图片上传成功，正在处理...</div>');
                    console.log(response.img_path);
                    process(response.img_path);
                } else {
                    $('#status').text('错误: ' + response.error);
                }
            },
            error: function () {
                $('#status').append('<div>请求失败，请重试。</div>');
            }
        });
    });

    // 处理图片
    function process(path) {
        console.log('process');
        console.log(path);
        var formdata = new FormData();
        formdata.append('path', path);
        $.ajax({
            url: 'process/',
            data: formdata,
            type: 'POST',
            contentType: false,
            processData: false,
            success:
                function (response) {
                    if (response.stat === 'completed') {
                        $('#response').append('<div>处理完成！</div>');
                        var resultDiv = $('#result');
                        resultDiv.empty();
                        // 遍历若干个识别结果
                        for (var i = 0; i < response.results.length; i++) {
                            // 添加表格
                            resultDiv.append('<table id="result_table"' + i + ' class="result_table"></table>');
                            // 获取到单个识别图片的分类结果
                            var results_dict = response.results[i];
                            // 构建表格主体
                            var table = resultDiv.children().last();
                            table.append('<tr><th>示例图片</th><th>识别结果</th></tr>');
                            for (var id in results_dict) {
                                var details = results_dict[id];
                                var imgSrc = "/static/images/" + id + ".jpg";

                                table.append(
                                    '<tr>' +
                                    '<td class="result_table_image">' +
                                    '<div class="example_image">' +
                                    '<img class="large_image" id="example_img' + id + '" src="' + imgSrc + '" alt="' + details[0] + '" onclick="seeBigImage()">' +
                                    '</div>' +
                                    '</td>' +

                                    '<td>' +
                                    '<div class="result_content">' +
                                    '<div class="result_title">' +
                                    '<strong>' +
                                    '名称:' +
                                    '</strong>' +
                                    details[0] +
                                    '<br>' +
                                    '</div>' +
                                    '<div class="result_content_column">' +
                                    '<strong>' +
                                    '栖息地:' +
                                    '</strong>' +
                                    details[1] +
                                    '<br>' +
                                    '<strong>' +
                                    '特征:' +
                                    '</strong>' +
                                    details[2] +
                                    '<br>' +
                                    '<strong>' +
                                    '建议:' +
                                    '</strong>' +
                                    details[3] +
                                    '<br>' +
                                    '<strong>' +
                                    '置信度:' +
                                    '</strong>' +
                                    details[4] +
                                    '<br>' +
                                    '<br>' +
                                    '</div>' +
                                    '</div>' +
                                    '</td>' +
                                    '</tr>'
                                );
                            }

                            // 显示原始图片
                            // 获取当前表格的第一个<tr>元素
                            var firstTr = table.find('tr').first();
                            // 创建一个新的<td>元素
                            var newTh = $('<th rowspan="' + table.find('tr').length + '"></th>');
                            // 创建一个包含<div>元素和<img>元素的<div>元素
                            var divElement = $('<div class="original_image"></div>');
                            var imgElement = $('<img>').attr('src', response.orig_images[i]); // 替换为你的图片路径
                            imgElement.attr('alt', '原始图片' + (i + 1)); // 设置图片的alt属性
                            // 为<img>元素添加点击事件
                            imgElement.click(seeBigImage);
                            // 将<img>元素添加到<div>元素中
                            divElement.append(imgElement);
                            // 将<div>元素添加到<td>元素中
                            newTh.append(divElement);
                            // 将新的<td>元素添加到第一个<tr>元素最开头，将图片呈现在页面左侧
                            firstTr.prepend(newTh);
                        }
                        // 显示结果框
                        resultDiv.css('display', 'block');
                        // 图片点击放大
                        $('img').each(function () {
                            var imgSrc = $(this).attr('src'); // 获取图片的相对src属性
                            var imgAlt = $(this).attr('alt'); // 获取图片的alt属性
                            // 创建一个包含图片的链接元素
                            $(this).wrap('<a href="' + imgSrc + '" data-fancybox="gallery" data-caption="' + imgAlt + '"></a>');
                        });
                    } else {
                        $('#status').append('<div>处理失败: ' + response.error+'</div>');
                    }
                }
        })
        ;
    }


});
