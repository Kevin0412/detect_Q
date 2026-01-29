#!/usr/bin/env bash
# scripts/reorg_images.sh
# 说明：此脚本用于将根目录下的 images* 文件夹按建议重组到 screenshots/ 子目录中。
# 默认运行在预览模式（DRY_RUN=1），仅打印将要执行的 mv 命令；设置 DRY_RUN=0 将真正执行移动。

set -euo pipefail

DRY_RUN=${DRY_RUN:-1}
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p screenshots/validation screenshots/env_variations screenshots/fitting screenshots/author_icons screenshots/archive

do_mv() {
  src="$1"
  dst="$2"
  if [ ! -e "$src" ]; then
    return
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY_RUN: mv '$src' '$dst'"
  else
    echo "MOVING: '$src' -> '$dst'"
    mv "$src" "$dst"
  fi
}

# 移动 images -> screenshots/validation
if [ -d images ]; then
  for f in images/*; do
    [ -e "$f" ] || continue
    do_mv "$f" screenshots/validation/
  done
else
  echo "目录 images 不存在，跳过。"
fi

# images_2, images_3 -> screenshots/env_variations
for src in images_2 images_3; do
  if [ -d "$src" ]; then
    for f in "$src"/*; do
      [ -e "$f" ] || continue
      do_mv "$f" screenshots/env_variations/
    done
  else
    echo "目录 $src 不存在，跳过。"
  fi
done

# images_4 -> screenshots/fitting
if [ -d images_4 ]; then
  for f in images_4/*; do
    [ -e "$f" ] || continue
    do_mv "$f" screenshots/fitting/
  done
else
  echo "目录 images_4 不存在，跳过。"
fi

# images_6 -> screenshots/author_icons
if [ -d images_6 ]; then
  for f in images_6/*; do
    [ -e "$f" ] || continue
    do_mv "$f" screenshots/author_icons/
  done
else
  echo "目录 images_6 不存在，跳过。"
fi

# images_5, images_7 -> screenshots/archive
for src in images_5 images_7; do
  if [ -d "$src" ]; then
    for f in "$src"/*; do
      [ -e "$f" ] || continue
      do_mv "$f" screenshots/archive/
    done
  else
    echo "目录 $src 不存在，跳过。"
  fi
done

# 结束提示
if [ "$DRY_RUN" -eq 1 ]; then
  echo "预览完成。确认无误后：运行 'DRY_RUN=0 bash scripts/reorg_images.sh' 来执行移动。"
else
  echo "移动完成。"
fi
