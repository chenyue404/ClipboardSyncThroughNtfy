# ClipboardSyncThroughNtfy
通过[ntfy](https://ntfy.sh/)来自动同步剪贴板，这个是Windows客户端，Android端直接用ntfy官方app配合tasker即可。

主要原理就是各端订阅同一个Topic，收到message就写入剪贴板。监听到剪贴板的变化，则发送一条Title为自己设备名的Message。这样通过Title即可区分不同的设备，从而避免自读自写的情况。

如果是使用的公共的ntfy服务器，可能会有隐私泄露的风险。可以在传输前对每一条message进行加密，收到后再解密。因为我是用的自己的服务器，所以懒得写相关代码了🤪
