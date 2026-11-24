package com.sportshop.service;

import com.sportshop.config.ShopProperties;
import com.sportshop.web.BadRequestException;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;
import org.springframework.stereotype.Service;

/** Lưu ảnh tải lên vào thư mục uploads. Nhận dạng định dạng theo nội dung tệp, không tin tên tệp. */
@Service
public class ImageStorageService {
    public static final int MAX_BYTES = 8_000_000;
    private final Path dir;

    public ImageStorageService(ShopProperties props) { this.dir = Path.of(props.uploadDir()).toAbsolutePath(); }

    public String save(byte[] data) {
        if (data.length > MAX_BYTES) throw new BadRequestException("image_too_large");
        String ext = sniff(data);
        if (ext == null) throw new BadRequestException("not_an_image");
        String name = UUID.randomUUID().toString().replace("-", "") + "." + ext;
        try {
            Files.createDirectories(dir);
            Files.write(dir.resolve(name), data);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
        return "/uploads/" + name;
    }

    static String sniff(byte[] b) {
        if (b.length < 12) return null;
        if ((b[0] & 0xff) == 0xff && (b[1] & 0xff) == 0xd8 && (b[2] & 0xff) == 0xff) return "jpg";
        if ((b[0] & 0xff) == 0x89 && b[1] == 'P' && b[2] == 'N' && b[3] == 'G') return "png";
        String head = new String(b, 0, 4, StandardCharsets.ISO_8859_1);
        if (head.equals("GIF8")) return "gif";
        if (head.equals("RIFF") && new String(b, 8, 4, StandardCharsets.ISO_8859_1).equals("WEBP")) return "webp";
        return null;
    }
}
