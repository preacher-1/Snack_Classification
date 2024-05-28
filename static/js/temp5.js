// 文件上传的间接调用
function button_click() {
    document.getElementById('file').click();
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
        // 清空上一次提交的状态信息
        $('#status').empty();
        $('#response').empty();
        $('#result').empty();
        var formdata = new FormData(), url;
        // 对于提供的信息形式，选择不同的处理方式
        if (this.image.files.length > 0) {
            url = 'preprocess/';
            formdata.append('data', this.image.files[0]);
        } else if (this.image_url.value !== '') {
            url = 'download/'
            formdata.append('data', this.image_url.value);
            $('#status').text('从' + this.image_url.value + '下载图片...');
            this.image_url.value = '';
        } else {
            alert('请选择图片或输入图片URL');
            return;
        }
        document.getElementById('imagePreview').innerHTML = '';
        this.reset();
        // var formData = new FormData(this);
        // $('#status').text('正在处理...');

        $.ajax({
            url: url,
            type: 'POST',
            data: formdata,
            contentType: false,
            processData: false,
            success: function (response) {
                if (response.stat === 'download_complete') {
                    $('#status').append('图片下载成功，已下载' + response.size + 'KB，用时' + response.used_time + '秒。');
                    process(response.img_path);
                } else if (response.stat === 'preprocess_complete') {
                    $('#status').text('图片上传成功');
                    console.log(response.img_path);
                    process(response.img_path);
                } else {
                    $('#status').text('错误: ' + response.error);
                }
            },
            error: function () {
                $('#status').text('请求失败，请重试。');
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
            url: 'process/', // '/task-status/' + taskId + '/',
            data: formdata,
            type: 'POST',
            contentType: false,
            processData: false,
            success:
                function (response) {
                    if (response.stat === 'completed') {
                        $('#response').text('处理完成！');
                        var resultDiv = $('#result');
                        resultDiv.empty();


                        resultDiv.append('<img src="' + response.orig_image + '" alt="Original Image">');
                        response.results.forEach(function (item) {
                            resultDiv.append('<table id="result_table" class="result_table"></table>>');
                            var table = resultDiv.children()[0];
                            for (var id in item) {
                                var details = item[id];
                                var imgSrc = "/static/images/" + id + ".jpg";
                                table.append(
                                    '<td class="result_table_image">' +
                                    '<div class="example_image">' +
                                    '<img id="example_img1" src="'+imgSrc+'" alt="example_img1">' +
                                    '</div>' +
                                    '</td>'+

                                    '<td>\n' +
                                    '<div class="result_content">\n' +
                                    '<div class="result_title">\n' +
                                    '<strong>\n' +
                                    'Desperados III\n' +
                                    '</strong>\n' +
                                    '<br>\n' +
                                    '</div>\n' +
                                    '                    <div class="result_content_column">\n' +
                                    '                        <strong>\n' +
                                    '                            名称:\n' +
                                    '                        </strong>\n' +
                                    '                        847488731\n' +
                                    '                        <br>\n' +
                                    '                        <strong>\n' +
                                    '                            栖息地:\n' +
                                    '                        </strong>\n' +
                                    '                        panpanchenchen\n' +
                                    '                        <br>\n' +
                                    '                        <strong>\n' +
                                    '                            特征:\n' +
                                    '                        </strong>\n' +
                                    '                        847488731\n' +
                                    '                        <br>\n' +
                                    '                        <strong>\n' +
                                    '                            建议:\n' +
                                    '                        </strong>\n' +
                                    '                        847488731\n' +
                                    '                        <br>\n' +
                                    '                        <strong>\n' +
                                    '                            置信度:\n' +
                                    '                        </strong>\n' +
                                    '                        847488731\n' +
                                    '                        <br>\n' +
                                    '                        <br>\n' +
                                    '                    </div>\n' +
                                    '                </div>\n' +
                                    '            </td>'
                                );
                            }
                        });
                    } else if (response.stat === 'failed') {
                        $('#status').text('处理失败: ' + response.error);
                    } else {
                        alert('未知错误: ' + response.error);
                    }
                }
        })
        ;
    }
});
