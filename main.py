from game import * # PlayerThread, MasterThread, GlobalObject, ReceptionThread

def init():
    pass

print_header = "[*] main.py:"

if __name__=="__main__":
    init()
    ## start
    # masterの起動
    master_ = MasterThread()
    master_.start()

    # 受付
    # reception をdemonでうごかす
    reception_ = ReceptionThread(port=12345, master_=master_)
    reception_.start()

    # 開始
    try:
        while not master_.global_object.end_flag:
            pass
    except KeyboardInterrupt:
        pass

    # 終了処理
    print(print_header, "end")
    
