from Scheduler import Scheduler


def main():
    try:
        Scheduler().run()
    except:
        print('运行失败，再次尝试运行')
        main()

if __name__ == '__main__':
    main()
