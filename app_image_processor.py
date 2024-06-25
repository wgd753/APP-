from PIL import Image
import os
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox
import shutil

def resize_and_compress_image(input_image_path, output_image_path, target_size, max_size_kb, status_bar_height=75):
    try:
        with Image.open(input_image_path) as image:
            # 转换图像模式为RGB，以防止JPEG保存错误
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # 去掉状态栏并保留从状态栏下方到图片底部的部分
            width, height = image.size
            cropped_image = image.crop((0, status_bar_height, width, height))

            # 获取裁剪后的宽高
            crop_width, crop_height = cropped_image.size
            
            # 调整图片尺寸并保持比例
            aspect_ratio = crop_width / crop_height
            target_width, target_height = target_size

            if target_width / target_height > aspect_ratio:
                resize_width = target_width
                resize_height = int(target_width / aspect_ratio)
            else:
                resize_height = target_height
                resize_width = int(target_height * aspect_ratio)

            resized_image = cropped_image.resize((resize_width, resize_height), Image.Resampling.LANCZOS)

            # 靠上居中裁剪以适应目标尺寸
            left = (resize_width - target_width) // 2
            top = 0  # 靠上对齐
            right = left + target_width
            bottom = top + target_height
            final_image = resized_image.crop((left, top, right, bottom))

            quality = 95
            while True:
                final_image.save(output_image_path, format='JPEG', quality=quality, optimize=True)
                if os.path.getsize(output_image_path) <= max_size_kb * 1024 or quality <= 10:
                    break
                quality -= 5
    except Exception as e:
        print(f"Error processing {input_image_path}: {e}")

def process_images(input_dir, output_base_dir, status_bar_height):
    sizes = [(450, 800, 2000), (720, 1280, 1000), (1080, 1920, 1000)]
    for size in sizes:
        output_dir = os.path.join(output_base_dir, f"{size[0]}x{size[1]}")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    image_files = [f for f in os.listdir(input_dir) if os.path.splitext(f)[1].lower() in Image.registered_extensions()]
    if not image_files:
        print("输入目录中没有找到图片文件。")
        return
    
    for image_name in image_files:
        input_image_path = os.path.join(input_dir, image_name)
        for size in sizes:
            output_dir = os.path.join(output_base_dir, f"{size[0]}x{size[1]}")
            output_image_path = os.path.join(
                output_dir, f"{os.path.splitext(image_name)[0]}_{size[0]}x{size[1]}{os.path.splitext(image_name)[1]}"
            )
            resize_and_compress_image(input_image_path, output_image_path, (size[0], size[1]), size[2], status_bar_height)
            print(f"Saved resized and compressed image to {output_image_path}")

def create_zip(output_base_dir, product_name):
    zip_filename = os.path.join(output_base_dir, f"{product_name}_上架图.zip")
    shutil.make_archive(zip_filename.replace('.zip', ''), 'zip', output_base_dir)
    print(f"压缩包已创建：{zip_filename}")

def main():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    try:
        # 获取实际脚本所在目录
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))

        # 使用脚本所在目录下的“截图”文件夹作为输入目录
        input_directory = os.path.join(script_dir, '截图')

        # 使用脚本所在目录下的“生成结果”文件夹作为输出基目录
        output_base_directory = os.path.join(script_dir, '生成结果')

        # 提示用户输入状态栏高度，默认值为75
        status_bar_height = simpledialog.askinteger("输入状态栏高度", "请输入安卓状态栏高度（像素），默认为75:", initialvalue=75)
        if status_bar_height is None:
            status_bar_height = 75

        # 提示用户输入产品名称
        product_name = simpledialog.askstring("输入产品名称", "请输入产品名称：")
        if not product_name:
            messagebox.showerror("错误", "产品名称不能为空")
            return

        # 创建产品名称目录
        product_dir = os.path.join(output_base_directory, product_name)
        if not os.path.exists(product_dir):
            os.makedirs(product_dir)

        # 检查输入目录是否存在，不存在则创建
        if not os.path.exists(input_directory):
            os.makedirs(input_directory)
            messagebox.showinfo("信息", f"输入目录 {input_directory} 创建成功，请将图片放入该文件夹后再运行脚本。")
        else:
            print(f"输入目录: {input_directory}")
            print(f"输出基目录: {output_base_directory}")
            print(f"产品目录: {product_dir}")
            print(f"状态栏高度: {status_bar_height}")
            process_images(input_directory, product_dir, status_bar_height)
            create_zip(product_dir, product_name)
            messagebox.showinfo("完成", "所有图片已处理完毕并已生成压缩包！")

    except Exception as e:
        messagebox.showerror("发生错误", f"发生错误: {e}")
        input("按任意键退出...")

if __name__ == "__main__":
    main()
