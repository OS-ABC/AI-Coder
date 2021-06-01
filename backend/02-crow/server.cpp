#include "crow.h"
#include "crow/query_string.h"
#include "Python.h"
#include<string>
#include<vector>
#include<iostream>

using namespace std;

//CPython编译：g++ -Wall -std=c++11  test.cpp -o 0test -fsanitize=leak -lpython3.6m
//crow编译：g++ -std=c++11 serve.cpp -o server -lpython3.6m -lboost_system -lboost_filesystem -L../boost/stage/lib -pthread

int main()
{
    //step1: PyC init.
    Py_Initialize();
    if(!Py_IsInitialized()){
        cout << "[error]: PyC init error." << endl;
        return 1;
    }
    cout << "[INFO]: PyC init succeed." << endl;

    //step2: Export serve.py path
    string work_path = string("sys.path.append(\'") + "\')";
    PyRun_SimpleString("import sys");
    PyRun_SimpleString(work_path.c_str());

    //step3: Import serve.py 
    PyObject* pModule = PyImport_ImportModule("serve");
    if(!pModule){
        cout << "[Error]: Import serve.py failed." << endl;
        return 1;
    }
    cout << "[INFO]: Import serve.py succeed." << endl;

    //step4: Get classes and methods from pModule
    PyObject *pDict = PyModule_GetDict(pModule);
    if(!pDict){
        cout << "[Error]: Get classes and methods from pModule failed." << endl;
        return 1;
    }
    cout << "[INFO]: Get classes and methods from pModule succeed." << endl;

    //step5: Get Server class
    PyObject* pClass = PyDict_GetItemString(pDict,"Server");
    if(!pClass){
        cout << "[Error]: Get Server class failed." << endl;
        return 1;
    }
    cout << "[INFO]: Get Server class succeed." << endl;

    //step6: Get server construct function
    PyObject *pConstruct = PyInstanceMethod_New(pClass);
    if(!pConstruct){
        cout << "[Error]: Get server construct function failed." << endl;
        return 1;
    }
    cout << "[INFO]: Get server construct function succeed." << endl;

    //step7: Create and init Server instance
    PyObject* pServer = PyObject_CallObject(pConstruct,nullptr);
    if(!pServer){
        cout << "[Error]: Create and init Server instance failed." << endl;
        return 1;
    }
    cout << "[INFO]: Create and init Server instance succeed." << endl;
    
    //step8: Crow start
    crow::SimpleApp app;

    CROW_ROUTE(app, "/")([](){
        return "Welcome to use the plugin!";
    });

    //step9: Model inference
    CROW_ROUTE(app, "/plugin_test")
    .methods("GET"_method)
    ([pServer](const crow::request& req){
        std::ostringstream os;
        crow::query_string keyword = req.url_params;
        for(char* str :keyword.get_key_value_pairs_()){
            if(strlen(str) == 0){
                cout << "Got a empty value." <<endl;
            }else{
                //cout << "Got keyword: " << str << endl;
                PyObject *pRet = PyObject_CallMethod(pServer,"reference", "s",str);
                if (pRet){
                    char* res;
                    PyArg_Parse(pRet,"s", &res);
                    //cout << "[INFO]: Got result succeed: " << res << endl;
                    os << res;
                    Py_DecRef(pRet);
                }else{
                    cout << "[Error]: Got result failed." << endl;
                }
            }
        }
        return crow::response{os.str()};
    });

    app.port(5000).multithreaded().run();

    Py_DecRef(pModule);
    Py_DecRef(pDict);
    Py_DecRef(pClass);
    Py_DecRef(pServer);
    Py_Finalize();
    return 0;
}