//package org.intellij.sdk.language;

import com.intellij.codeInsight.completion.*;
import com.intellij.codeInsight.lookup.LookupElement;
import com.intellij.codeInsight.lookup.LookupElementBuilder;
import com.intellij.openapi.editor.Document;
import com.intellij.openapi.editor.Editor;
import com.intellij.patterns.PlatformPatterns;
import com.intellij.patterns.PsiElementPattern;
import com.intellij.psi.PsiPlainText;
import com.intellij.util.ProcessingContext;
import org.jetbrains.annotations.NotNull;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import net.sf.json.JSONArray;
import net.sf.json.JSONObject;
import org.jetbrains.annotations.Nullable;
import java.util.Iterator;
import java.util.Map;

public class SimpleCompletionContributor extends CompletionContributor{


    @Override
    public void fillCompletionVariants(@NotNull CompletionParameters parameters, @NotNull CompletionResultSet result) {

        Document document = parameters.getEditor().getDocument();
        String str = document.getText();
        String strs[] = str.split("\n");
        String key = "";
        String new_line = "";
        String ori_line = "";
        String end_char = " ,.=()[]{}:";
        //抽取上文代码句逻辑
        int sentence_nums = 10;
        ori_line = strs[strs.length - 1];

        //文本生成模型防止过度调用
        String c = ori_line.substring(ori_line.length()-1);
        //System.out.println("ori_line: " + ori_line + ", end char: " + c);
        if(!end_char.contains(c)){
            //System.out.println("不符合调用条件！");
            return;
        }


        new_line = ori_line.trim();
        for(int i = 2;i <= strs.length && sentence_nums > 0;++i){
            String line = strs[strs.length - i].trim();
            if(line.length() > 3){
                key = line + "\n" + key;
                sentence_nums--;
            }
        }
        //网页会自动将空格编解码为%20
        key = key.replaceAll(" ","%20");
        System.out.println("key: " + key);

        try{
            String urlStr = "http://xx.xx.xx.xx:5000/plugin_test";
            JSONObject jsonObject = null;
            URL url = new URL(urlStr);
            //创建http链接
            HttpURLConnection httpURLConnection = (HttpURLConnection) url.openConnection();
            //设置请求的方法类型
            httpURLConnection.setRequestMethod("POST");
            // Post请求不能使用缓存
            httpURLConnection.setUseCaches(false);
            //设置请求的内容类型
            httpURLConnection.setRequestProperty("Content-type", "application/json");
            //设置发送数据
            httpURLConnection.setDoOutput(true);
            //设置接受数据
            httpURLConnection.setDoInput(true);

            //设置body内的参数，put到JSONObject中
            JSONObject param = new JSONObject();
            param.put("type","Text_Gen");
            param.put("data",key + "\n" + new_line);

            //param.put("type","Seq2Seq");
            //param.put("data",key);

            // 建立实际的连接
            httpURLConnection.connect();
            // 得到请求的输出流对象
            OutputStreamWriter writer = new OutputStreamWriter(httpURLConnection.getOutputStream(),"UTF-8");
            writer.write(param.toString());
            writer.flush();

            //接收数据
            InputStream inputStream = httpURLConnection.getInputStream();
            //定义字节数组
            byte[] b = new byte[1024];
            //定义一个输出流存储接收到的数据
            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            //开始接收数据
            int len = 0;
            while (true) {
                len = inputStream.read(b);
                if (len == -1) {
                    //数据读完
                    break;
                }
                byteArrayOutputStream.write(b, 0, len);
            }
            //从输出流中获取读取到数据(服务端返回的)
            String response = byteArrayOutputStream.toString();
            //System.out.println("response:"+response);
            jsonObject = JSONObject.fromObject(response);
            //遍历JSON对象
            Iterator iter = jsonObject.entrySet().iterator();
            while (iter.hasNext()) {
                Map.Entry entry = (Map.Entry) iter.next();
                //System.out.println(entry.getKey().toString());
                String completion_result = entry.getValue().toString();
                //System.out.println("data:"+completion_result);
                if(new_line.length() < completion_result.length()){
                    String completion_result_start = completion_result.substring(0,new_line.length());
                    //System.out.println("new_line: " + new_line + ",completion_result_start:"+ completion_result_start);
                    if(new_line.equals(completion_result_start))
                        completion_result = completion_result.substring(new_line.length());
                }
                result.addElement(LookupElementBuilder.create(completion_result.trim()));
            }

            //byteArrayOutputStream.close();
            // 关闭连接
            httpURLConnection.disconnect();

        }catch(IOException e){
            e.printStackTrace();
        }
        super.fillCompletionVariants(parameters, result);
    }
}
