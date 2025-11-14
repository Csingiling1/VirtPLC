package com.virtplc.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Dashboard model for storing user-created dashboards
 */
@Entity
@Table(name = "dashboards")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Dashboard {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(length = 1000)
    private String description;

    @Column(columnDefinition = "TEXT")
    private String itemsJson; // Store items as JSON

    @Column(nullable = false)
    private Integer gridSize;

    @Column(nullable = false)
    private Boolean autoTile;

    @Column(nullable = false)
    private String userId;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column
    private LocalDateTime updatedAt;

    @Column(nullable = false)
    @Builder.Default
    private Boolean isPublic = false;

    // Transient field for runtime use
    @Transient
    private List<CanvasItem> items;

    /**
     * Canvas item representing a component on the dashboard
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CanvasItem {
        private String id;
        private String type; // 'factory', 'device', 'signal', 'chart', 'gauge', 'button'
        private Object data; // The actual data object (Factory, Device, Signal, etc.)
        private Integer x;
        private Integer y;
        private Integer width;
        private Integer height;
        private Integer gridX;
        private Integer gridY;
        private Integer gridWidth;
        private Integer gridHeight;
    }
}